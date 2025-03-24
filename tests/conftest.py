import pytest
from config import TestConfig  # Ensure the correct package path

@pytest.fixture(scope="session")
def test_config():
    return TestConfig

@pytest.fixture(scope="session")
def api_credentials():
    return {
        "api_key": TestConfig.API_KEY,
        "api_url": TestConfig.API_URL
    }

@pytest.fixture(scope="session")
def simple_storage_service():
    from salad_cloud_transcription_sdk.services.simple_storage import SimpleStorageService
    return SimpleStorageService(
        base_url=TestConfig.S4_API_URL,
        api_key=TestConfig.API_KEY
    )
