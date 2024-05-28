import os

class Config:
    SECRET_KEY = os.getenv('API_SECRET_KEY', 'your_default_secret_key')
    SYNC_LOCAL_SPEC = True
    LOCAL_SPEC_PATH = os.path.join(os.path.dirname(__file__), 'openapi.json')
    LOCAL_SPEC_INDENT = 4
    DEBUG = True

