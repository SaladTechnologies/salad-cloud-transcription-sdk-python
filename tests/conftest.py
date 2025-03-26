import os
import json
import pytest
import pytest_asyncio
from config import TestConfig
from salad_cloud_transcription_sdk.services.transcription import (
    TranscriptionService,
)
from salad_cloud_transcription_sdk.services.simple_storage import (
    SimpleStorageService,
)
from salad_cloud_transcription_sdk.services.async_.transcription import (
    TranscriptionServiceAsync,
)
from salad_cloud_transcription_sdk.services.async_.simple_storage import (
    SimpleStorageServiceAsync,
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


@pytest.fixture(scope="session")
def webhook_data():
    with open(
        os.path.join("tests", "data", "webhooks.json"), "r", encoding="utf-8"
    ) as f:
        return json.load(f)


@pytest_asyncio.fixture
async def transcription_service_async():
    service = TranscriptionServiceAsync(api_key=TestConfig.API_KEY)
    yield service


@pytest_asyncio.fixture
async def simple_storage_service_async():
    service = SimpleStorageServiceAsync(api_key=TestConfig.API_KEY)
    yield service
