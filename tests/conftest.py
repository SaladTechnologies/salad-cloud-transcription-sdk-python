import pytest
from config import TestConfig
from salad_cloud_transcription_sdk.services.transcription import (
    TranscriptionService,
)
from salad_cloud_transcription_sdk.services.simple_storage import (
    SimpleStorageService,
)


@pytest.fixture(scope="session")
def test_config():
    return TestConfig


@pytest.fixture(scope="session")
def api_credentials():
    return {"api_key": TestConfig.API_KEY, "api_url": TestConfig.API_URL}


@pytest.fixture(scope="session")
def simple_storage_service():
    return SimpleStorageService(
        base_url=TestConfig.S4_API_URL, api_key=TestConfig.API_KEY
    )


@pytest.fixture(scope="session")
def transcription_service():
    return TranscriptionService(api_key=TestConfig.API_KEY, base_url=TestConfig.API_URL)
