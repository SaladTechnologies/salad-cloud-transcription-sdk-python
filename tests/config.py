import os
from dotenv import load_dotenv

# Load environment variables from .env.development file
load_dotenv('.env.development')

# Configuration class for test settings
class TestConfig:
    # API settings
    API_KEY = os.environ.get('SALAD_API_KEY', 'default_key')
    API_URL = os.environ.get('SALAD_API_URL', 'https://default-api.example.com')
    S4_API_URL = os.environ.get('SALAD_S4_API_URL', 'https://default-s4-api.example.com')
    ORGANIZATION_NAME = os.environ.get('SALAD_ORGANIZATION_NAME', 'salad')
    
    # Other test settings
    TIMEOUT = int(os.environ.get('TIMEOUT', '30'))
    MAX_RETRIES = int(os.environ.get('MAX_RETRIES', '3'))
    TEST_DATA_PATH = os.environ.get('TEST_DATA_PATH', 'tests/data')
