import uuid
import json
from datetime import datetime, timedelta
from .extensions import celery, db, mail
from .models import Control, Alerta, Recorrido, Usuario
from openai import OpenAI
from flask import current_app
from flask_mail import Message

@celery.task(name='tasks.procesar_foto')
def procesar_foto(file_key: str):
    """
    A background task to process a photo.
    For now, it's just a placeholder.
    """
    print(f"Procesando foto: {file_key}")
    # In a real scenario, you'd use boto3 to interact with S3
    print(f"Foto {file_key} procesada.")
    return f"processed_{file_key}"

@celery.task(name='tasks.analizar_control')
def analizar_control(control_id_str: str):
    """
    Analyzes a control object and creates an Alerta if necessary.
    """
    from . import create_app # Local import to avoid circular dependency at module level
    app = create_app()
    with app.app_context():
        try:
            control_id = uuid.UUID(control_id_str)
            control = db.session.get(Control, control_id)
            if not control:
                print(f"Control with id {control_id_str} not found.")
                return

            # Example logic: check for low fluid levels
            if control.tipo == 'fluidos' and isinstance(control.detalle, dict):
                for key, value in control.detalle.items():
                    if value == 'bajo':
                        mensaje = f"Nivel bajo detectado para '{key}' en el vehículo."
                        alerta = Alerta(
                            recorrido_id=control.recorrido_id,
                            mensaje=mensaje
                        )
                        db.session.add(alerta)
                        print(f"Alerta creada: {mensaje}")

            db.session.commit()
        except Exception as e:
            print(f"Error analyzing control {control_id_str}: {e}")
            db.session.rollback()

@celery.task(name='tasks.extract_receipt_data')
def extract_receipt_data(recorrido_id_str: str, image_url: str):
    """
    Uses OpenAI's vision model to extract data from a fuel receipt image.
    """
    from . import create_app
    app = create_app()
    with app.app_context():
        try:
            client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract the total cost and the total liters from this fuel receipt. Provide the answer as a JSON object with two keys: 'costo_total' and 'litros_totales'. The values should be numbers only, without currency symbols. If you cannot find a value, use null."},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            result_str = response.choices[0].message.content
            result_json = json.loads(result_str)

            recorrido_id = uuid.UUID(recorrido_id_str)
            recorrido = db.session.get(Recorrido, recorrido_id)
            if not recorrido:
                print(f"Recorrido {recorrido_id_str} not found for OCR update.")
                return

            costo = result_json.get('costo_total')
            litros = result_json.get('litros_totales')

            if costo is not None:
                recorrido.combustible_costo = costo
            if litros is not None:
                recorrido.combustible_litros = litros

            db.session.commit()
            print(f"Recorrido {recorrido_id_str} updated with OCR data: Costo={costo}, Litros={litros}")

        except Exception as e:
            print(f"Error processing receipt for recorrido {recorrido_id_str}: {e}")
            db.session.rollback()

@celery.task(name='tasks.generate_weekly_report')
def generate_and_email_report():
    """
    Generates a weekly summary report using AI and emails it to admins.
    """
    from . import create_app
    app = create_app()
    with app.app_context():
        try:
            # 1. Fetch data for the last week
            one_week_ago = datetime.utcnow() - timedelta(days=7)
            recorridos = Recorrido.query.filter(Recorrido.fecha_inicio >= one_week_ago).all()

            if not recorridos:
                print("No recorridos in the last week. No report to send.")
                return

            # 2. Format data for AI prompt
            report_data = (
                f"Datos de recorridos de la última semana "
                f"({one_week_ago.strftime('%Y-%m-%d')} a {datetime.utcnow().strftime('%Y-%m-%d')}):\n"
            )
            report_data += f"- Total de recorridos: {len(recorridos)}\n"
            total_km = sum([(r.km_final - r.km_inicial) for r in recorridos if r.km_final and r.km_inicial] or [0])
            report_data += f"- Total KM recorridos: {total_km:.2f}\n"
            total_costo_combustible = sum([r.combustible_costo for r in recorridos if r.combustible_costo] or [0])
            report_data += f"- Costo total de combustible: ${total_costo_combustible:.2f}\n"

            alertas = Alerta.query.filter(Alerta.creado_en >= one_week_ago).count()
            report_data += f"- Total de alertas generadas: {alertas}\n"

            prompt = (
                "Eres un gerente de flota. A partir de los siguientes datos semanales, "
                "escribe un breve informe ejecutivo para la dirección. Incluye un resumen de la actividad, "
                "identifica 1-2 tendencias o problemas clave (por ejemplo, alto consumo de combustible, muchas alertas), "
                f"y sugiere 2-3 acciones concretas a tomar.\n\n{report_data}"
            )

            # 3. Call OpenAI API
            client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            ai_summary = response.choices[0].message.content

            # Convert line breaks for HTML
            ai_summary_html = ai_summary.replace("\n", "<br>")

            # 4. Send email
            admin_emails = [user.email for user in Usuario.query.filter_by(rol='admin', activo=True).all()]
            if not admin_emails:
                print("No admin emails found to send report.")
                return

            msg = Message(
                subject="Informe Semanal de Flota Vehicular",
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=admin_emails,
                html=f"<h1>Informe Semanal</h1><p>{ai_summary_html}</p>"
            )
            mail.send(msg)
            print(f"Weekly report sent to {len(admin_emails)} admins.")

        except Exception as e:
            print(f"Error generating weekly report: {e}")
