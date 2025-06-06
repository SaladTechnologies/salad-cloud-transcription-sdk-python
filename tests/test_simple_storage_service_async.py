import json
import os
import tempfile
from urllib.parse import urlparse
import pytest
import pytest_asyncio
from salad_cloud_transcription_sdk.models.file_operation_response import (
    FileOperationResponse,
)
from salad_cloud_transcription_sdk.net.transport.request_error import RequestError
from salad_cloud_transcription_sdk.services.async_.simple_storage import (
    SimpleStorageServiceAsync,
)
from .config import TestConfig


@pytest.mark.asyncio
async def test_upload_small_file_with_signature_async(simple_storage_service_async):
    """Test that we can upload a small file with a signature."""

    local_file_path = os.path.join("tests", "data", "small_video.mp4")

    try:
        # Upload the file with signature
        try:
            repsonse = await simple_storage_service_async.upload_file(
                organization_name=TestConfig.ORGANIZATION_NAME,
                local_file_path=local_file_path,
                mime_type="video/mp4",
                sign=True,
                signature_exp=3600,  # 1 hour expiration
            )

            # Assert that the URL is returned
            assert repsonse is not None
            assert isinstance(repsonse, FileOperationResponse)
            assert repsonse.url is not None

            print(repsonse.url)
        except RequestError as e:
            error_details = {"message": str(e), "response_body": e.response.__str__()}
            print(f"RequestError: {json.dumps(error_details, indent=4)}")
            raise
    finally:
        pass


@pytest.mark.asyncio
# @pytest.mark.skip(
#     reason="Skipping this because it requires a large file to be placed on disk and configured here"
# )
async def test_upload_large_file_with_signature_async(simple_storage_service_async):
    """Test that we can upload a large file by using the chunked upload logic."""

    base_path = r"C:\Users\marcel\Downloads"
    local_file_path = os.path.join(base_path, "Win64OpenSSL-3_4_1.zip")

    try:
        # Upload the file with signature
        try:
            repsonse = await simple_storage_service_async.upload_file(
                organization_name=TestConfig.ORGANIZATION_NAME,
                local_file_path=local_file_path,
                mime_type="video/mp4",
                sign=True,
                signature_exp=3600,  # 1 hour expiration
            )

            # Assert that the URL is returned
            assert repsonse is not None
            assert isinstance(repsonse, FileOperationResponse)
            assert repsonse.url is not None

            print(repsonse.url)
        except RequestError as e:
            error_details = {"message": str(e), "response_body": e.response.__str__()}
            print(f"RequestError: {json.dumps(error_details, indent=4)}")
            raise
    finally:
        pass
