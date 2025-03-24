import json
import os
import tempfile
from config import TestConfig

# Import RequestError from the SDK
from salad_cloud_transcription_sdk.models.file_upload_response import FileUploadResponse
from salad_cloud_transcription_sdk.net.transport import RequestError


def test_upload_small_file_no_signature(simple_storage_service):
    """Test that we can upload a file using SimpleStorageService."""

    # Create a temporary file on disk
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        temp_file.write(b"Test file content")
        local_file_path = temp_file.name

    try:
        # Upload the file
        try:
            repsonse = simple_storage_service.upload_file(
                organization_name=TestConfig.ORGANIZATION_NAME,
                local_file_path=local_file_path,
                sign=False,
                mime_type="text/plain",
            )

            assert repsonse is not None
            assert isinstance(repsonse, FileUploadResponse)
            assert repsonse.url is not None

            print(repsonse.url)
        except RequestError as e:
            error_details = {"message": str(e), "response_body": e.response.__str__()}
            print(f"RequestError: {json.dumps(error_details, indent=4)}")
            raise  # Re-raise the exception after printing details
    finally:
        # Clean up the temporary file
        if os.path.exists(local_file_path):
            os.unlink(local_file_path)


def test_upload_small_file_with_signature(simple_storage_service):
    """Test that we can upload a file with a signature."""

    # Create a temporary file on disk
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        temp_file.write(b"Test file content with signature")
        local_file_path = temp_file.name

    try:
        # Upload the file with signature
        try:
            repsonse = simple_storage_service.upload_file(
                organization_name=TestConfig.ORGANIZATION_NAME,
                local_file_path=local_file_path,
                mime_type="text/plain",
                sign=True,
                signature_exp=3600,  # 1 hour expiration
            )

            # Assert that the URL is returned
            assert repsonse is not None
            assert isinstance(repsonse, FileUploadResponse)
            assert repsonse.url is not None

            print(repsonse.url)
        except RequestError as e:
            error_details = {"message": str(e), "response_body": e.response.__str__()}
            print(f"RequestError: {json.dumps(error_details, indent=4)}")
            raise  # Re-raise the exception after printing details
    finally:
        # Clean up the temporary file
        if os.path.exists(local_file_path):
            os.unlink(local_file_path)


def test_upload_large_file_with_signature(simple_storage_service):
    """Test that we can upload a large file with a signature."""

    # Use an existing video file
    local_file_path = os.path.join("tests", "data", "small_video.mp4")

    try:
        # Upload the file with signature
        try:
            repsonse = simple_storage_service.upload_file(
                organization_name=TestConfig.ORGANIZATION_NAME,
                local_file_path=local_file_path,
                mime_type="video/mp4",
                sign=True,
                signature_exp=3600,  # 1 hour expiration
            )

            # Assert that the URL is returned
            assert repsonse is not None
            assert isinstance(repsonse, FileUploadResponse)
            assert repsonse.url is not None

            print(repsonse.url)
        except RequestError as e:
            error_details = {"message": str(e), "response_body": e.response.__str__()}
            print(f"RequestError: {json.dumps(error_details, indent=4)}")
            raise  # Re-raise the exception after printing details
    finally:
        # No need to delete the file as it's not temporary
        pass
