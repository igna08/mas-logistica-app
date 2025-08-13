import os
from dotenv import load_dotenv

# Load environment variables from .env file at the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print("Loaded .env file")

from app import create_app

# Get config name from environment or use 'development'
config_name = os.getenv('FLASK_CONFIG') or 'development'
app = create_app(config_name)

if __name__ == '__main__':
    # Note: debug=True is set by the DevelopmentConfig
    # Running with host='0.0.0.0' makes it accessible on the network
    app.run(host='0.0.0.0', port=5000)
