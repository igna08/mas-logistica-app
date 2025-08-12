import os
from app import create_app
from app.extensions import celery

flask_app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# The Celery object is already initialized in extensions.py and configured in create_app
# We just need to make sure the tasks are run within the Flask app context.

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

# You can import task modules here to make sure they are registered
# For example: from app import tasks

# Example task from the user prompt, defined here for simplicity for now
@celery.task(name='tasks.procesar_foto')
def procesar_foto(file_key: str):
    """
    A background task to process a photo.
    For now, it's just a placeholder.
    In a real scenario, this would download from S3, process, and upload back.
    """
    print(f"Procesando foto: {file_key}")
    # from app.extensions import s3_client
    # s3_client.download(...)
    # ... process image ...
    # s3_client.upload(...)
    print(f"Foto {file_key} procesada.")
    return f"processed_{file_key}"
