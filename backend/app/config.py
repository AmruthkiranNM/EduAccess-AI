import os
from dotenv import load_dotenv

# Load environment variables from the root .env file
root_env = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
if os.path.exists(root_env):
    load_dotenv(root_env)

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DEBUG = os.getenv("FLASK_ENV") == "development"
    # Base paths
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
    TEMPLATE_DIR = os.path.join(FRONTEND_DIR, 'templates')
    STATIC_DIR = os.path.join(FRONTEND_DIR, 'static')
