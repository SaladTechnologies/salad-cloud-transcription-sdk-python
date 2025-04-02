import os
import tempfile
import pytest
import json
import pytest_asyncio
from salad_cloud_transcription_sdk.models.transcription_job_input import (
    TranscriptionJobInput,
    TranslationLanguage,
)
from salad_cloud_sdk.net.transport.request_error import RequestError
from salad_cloud_transcription_sdk.services.async_.transcription import (
    TranscriptionServiceAsync,
)
from salad_cloud_transcription_sdk.models.transcription_request import (
    TranscriptionRequest,
)
from .config import TestConfig


@pytest.mark.asyncio
async def test_transcribe_local_file_async(transcription_service_async):
    """Test transcribing a local file using async service"""
    request = TranscriptionRequest(
        options=TranscriptionJobInput(
            language_code="en",
            return_as_file=False,
            translate="to_eng",
            sentence_level_timestamps=True,
            word_level_timestamps=True,
            diarization=True,
            sentence_diarization=True,
            srt=True,
            summarize=100,
            custom_vocabulary="",
            llm_translation=[
                TranslationLanguage.SPANISH,
                TranslationLanguage.FRENCH,
                TranslationLanguage.GERMAN,
                TranslationLanguage.THAI,
            ],
            srt_translation=[
                TranslationLanguage.SPANISH,
                TranslationLanguage.FRENCH,
                TranslationLanguage.GERMAN,
                TranslationLanguage.THAI,
            ],
        ),
        metadata={"test_id": "integration_test", "environment": "testing"},
    )

    local_file_path = os.path.join("tests", "data", "small_video.mp4")

    try:
        job = await transcription_service_async.transcribe(
            source=local_file_path,
            organization_name=TestConfig.ORGANIZATION_NAME,
            auto_poll=True,
            request=request,
        )

        print(job)
    except RequestError as e:
        error_details = {"message": str(e), "response_body": e.response.__str__()}
        print(f"RequestError: {json.dumps(error_details, indent=4)}")
        raise

    # Assert that we got a job back with an ID
    assert job is not None
    assert job.id_ is not None

    # Verify we can retrieve the job
    retrieved_job = await transcription_service_async.get_transcription_job(
        organization_name=TestConfig.ORGANIZATION_NAME, job_id=job.id_
    )

    assert retrieved_job.id_ == job.id_


@pytest.mark.skip(
    reason="Skipping this because it requires a webhook to be configured manually"
)
@pytest.mark.asyncio
async def test_transcribe_local_file_with_webhook_async(transcription_service_async):
    """Test transcribing a local file with webhook using async service"""
    request = TranscriptionRequest(
        options=TranscriptionJobInput(
            language_code="en",
            return_as_file=False,
            translate="to_eng",
            sentence_level_timestamps=True,
            word_level_timestamps=True,
            diarization=True,
            sentence_diarization=True,
            srt=True,
            summarize=100,
            custom_vocabulary="",
            llm_translation=[
                TranslationLanguage.SPANISH,
                TranslationLanguage.FRENCH,
                TranslationLanguage.GERMAN,
                TranslationLanguage.THAI,
            ],
            srt_translation=[
                TranslationLanguage.SPANISH,
                TranslationLanguage.FRENCH,
                TranslationLanguage.GERMAN,
                TranslationLanguage.THAI,
            ],
        ),
        metadata={"test_id": "integration_test", "environment": "testing"},
        webhook="",
    )

    local_file_path = os.path.join("tests", "data", "small_video.mp4")

    try:
        job = await transcription_service_async.transcribe(
            source=local_file_path,
            organization_name=TestConfig.ORGANIZATION_NAME,
            auto_poll=False,
            request=request,
        )

        print(job)
    except RequestError as e:
        error_details = {"message": str(e), "response_body": e.response.__str__()}
        print(f"RequestError: {json.dumps(error_details, indent=4)}")
        raise

    # Assert that we got a job back with an ID
    assert job is not None
    assert job.id_ is not None

    # Verify we can retrieve the job
    retrieved_job = await transcription_service_async.get_transcription_job(
        organization_name=TestConfig.ORGANIZATION_NAME, job_id=job.id_
    )

    assert retrieved_job.id_ == job.id_
