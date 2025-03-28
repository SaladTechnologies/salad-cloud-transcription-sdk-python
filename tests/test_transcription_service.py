import os
import tempfile
import pytest
import json
from salad_cloud_transcription_sdk.models.transcription_job_file_output import (
    TranscriptionJobFileOutput,
)
from salad_cloud_transcription_sdk.models.transcription_job_input import (
    TranscriptionJobInput,
    TranslationLanguage,
)
from salad_cloud_sdk.net.transport.request_error import RequestError
from salad_cloud_transcription_sdk.models.transcription_job_output import (
    TranscriptionJobOutput,
)
from salad_cloud_transcription_sdk.services.transcription import TranscriptionService
from salad_cloud_transcription_sdk.models.transcription_request import (
    TranscriptionRequest,
)
from salad_cloud_transcription_sdk.services.simple_storage import SimpleStorageService
from .config import TestConfig


def test_transcribe_local_file(transcription_service):
    """Test transcribing a local file"""
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
        job = transcription_service.transcribe(
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

    assert isinstance(job.output, TranscriptionJobOutput)
    assert isinstance(job.output.text, str)
    assert isinstance(job.output.word_segments, list)
    assert isinstance(job.output.sentence_level_timestamps, list)
    assert isinstance(job.output.srt_content, str)
    assert isinstance(job.output.duration_in_seconds, float)

    # Verify we can retrieve the job
    retrieved_job = transcription_service.get_transcription_job(
        organization_name=TestConfig.ORGANIZATION_NAME, job_id=job.id_
    )

    assert retrieved_job.id_ == job.id_


@pytest.mark.skip(
    reason="Skipping this because it requires a webhook to be configured manually"
)
def test_transcribe_local_file_with_webhook(transcription_service):
    """Test transcribing a local file"""
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
        webhook="https://webhook.site/a8efbfcb-6b57-49f2-a389-5e58f3a6cb45",
    )

    local_file_path = os.path.join("tests", "data", "small_video.mp4")

    try:
        job = transcription_service.transcribe(
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
    retrieved_job = transcription_service.get_transcription_job(
        organization_name=TestConfig.ORGANIZATION_NAME, job_id=job.id_
    )

    assert retrieved_job.id_ == job.id_


def test_transcribe_remote_file(transcription_service, simple_storage_service):
    """Test transcribing a remote file"""
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
        upload_response = simple_storage_service.upload_file(
            organization_name=TestConfig.ORGANIZATION_NAME,
            local_file_path=local_file_path,
            mime_type="video/mp4",
            sign=True,
            signature_exp=3600,  # 1 hour expiration
        )

        remote_file_url = upload_response.url

        job = transcription_service.transcribe(
            source=remote_file_url,
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
    assert isinstance(job.output, TranscriptionJobOutput)
    assert isinstance(job.output.text, str)
    assert isinstance(job.output.word_segments, list)
    assert isinstance(job.output.sentence_level_timestamps, list)
    assert isinstance(job.output.srt_content, str)
    assert isinstance(job.output.duration_in_seconds, float)

    # Verify we can retrieve the job
    retrieved_job = transcription_service.get_transcription_job(
        organization_name=TestConfig.ORGANIZATION_NAME, job_id=job.id_
    )

    assert retrieved_job.id_ == job.id_
    assert isinstance(retrieved_job.output, TranscriptionJobOutput)
    assert isinstance(retrieved_job.output.text, str)
    assert isinstance(retrieved_job.output.word_segments, list)
    assert isinstance(retrieved_job.output.sentence_level_timestamps, list)
    assert isinstance(retrieved_job.output.srt_content, str)
    assert isinstance(retrieved_job.output.duration_in_seconds, float)


def test_transcribe_should_return_file(transcription_service):
    """Test transcribing a local file and returning a file"""
    request = TranscriptionRequest(
        options=TranscriptionJobInput(
            language_code="en",
            return_as_file=True,
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
        job = transcription_service.transcribe(
            source=local_file_path,
            organization_name=TestConfig.ORGANIZATION_NAME,
            auto_poll=True,
            request=request,
        )

    except RequestError as e:
        error_details = {"message": str(e), "response_body": e.response.__str__()}
        print(f"RequestError: {json.dumps(error_details, indent=4)}")
        raise

    # Assert that we got a job back with an ID
    assert job is not None
    assert job.id_ is not None

    assert isinstance(job.output, TranscriptionJobFileOutput)
    assert isinstance(job.output.url, str)
    assert isinstance(job.output.duration_in_seconds, float)

    # Verify we can retrieve the job
    retrieved_job = transcription_service.get_transcription_job(
        organization_name=TestConfig.ORGANIZATION_NAME, job_id=job.id_
    )

    assert isinstance(retrieved_job.output, TranscriptionJobFileOutput)
    assert isinstance(retrieved_job.output.url, str)
    assert isinstance(retrieved_job.output.duration_in_seconds, float)

    assert retrieved_job.id_ == job.id_
