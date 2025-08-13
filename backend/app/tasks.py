import uuid
from .extensions import celery, db
from .models import Control, Alerta

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
