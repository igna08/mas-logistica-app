import uuid
import json
from .extensions import celery, db
from .models import Control, Alerta, Recorrido
from openai import OpenAI
from flask import current_app

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
