import os
from app import create_app, celery

# Create a Flask app instance
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# The Celery object is already initialized in extensions.py and configured in create_app
# We just need to make sure the tasks are run within the Flask app context.
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

# To ensure tasks are registered, you can import the tasks module
from app import tasks

# Add the beat schedule
celery.conf.beat_schedule = {
    'send-weekly-report': {
        'task': 'tasks.generate_weekly_report',
        'schedule': 3600.0 * 24 * 7, # every 7 days
        # For more complex schedules, use crontab:
        # from celery.schedules import crontab
        # 'schedule': crontab(hour=7, day_of_week=1), # Every Monday at 7am
    },
}
celery.conf.timezone = 'UTC'
