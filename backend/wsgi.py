import os
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # This is for production environments where .env might not be present
    print("Warning: .env file not found.")


from app import create_app

# Get config name from environment or use default
config_name = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(config_name)
