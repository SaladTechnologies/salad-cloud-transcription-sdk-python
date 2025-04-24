# Salad Cloud Transcription SDK for Python

A Python SDK for interacting with the Salad Cloud Transcription service, which provides speech-to-text capabilities.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Sample Usage](#sample-usage)
  - [Start a Transcription Job and Wait for Completion](#start-a-transcription-job-and-wait-for-completion)
  - [Start a Transcription Job and Poll for Status](#start-a-transcription-job-and-poll-for-status)
  - [Start a Transcription Job and Get Updates via Webhook](#start-a-transcription-job-and-get-updates-via-webhook)
- [Development and Testing](#development-and-testing)
- [License](#license)
- [Support](#support)

## Installation

Install the package using pip:

```bash
pip install salad-cloud-transcription
```

## Quick Start

```python
from salad_cloud_transcription import SaladCloudTranscriptionSdk
from salad_cloud_transcription_sdk.models.transcription_engine import TranscriptionEngine
from salad_cloud_transcription_sdk.models.transcription_request import TranscriptionRequest
from salad_cloud_transcription_sdk.models.transcription_job_input import TranscriptionJobInput

# Initialize the SDK
sdk = SaladCloudTranscriptionSdk(api_key="your_api_key")

# Setup the request
request_object = TranscriptionRequest(
    options=TranscriptionJobInput(
        language_code="en",
        return_as_file=False,
        sentence_level_timestamps=True,
        word_level_timestamps=True,
        diarization=True,
        srt=True
    ),
    metadata={"project": "example_project"}
)

# Transcribe a video file using the Complete Transcription engine
result = sdk.transcription_client.transcribe(
    "path/to/video.mp4",
    organization_name="your_organization_name",
    request=request_object,
    engine=TranscriptionEngine.Complete,
    auto_poll=True
)

# Print the transcription
print(result.text)
```

## Authentication

### API Key Authentication

The Salad Cloud Transcription API uses API keys as a form of authentication. An API key is a unique identifier used to authenticate a user, developer, or a program that is calling the API.

### Setting the API Key

When you initialize the SDK, you can set the API key as follows:

```python
sdk = SaladCloudTranscriptionSdk(api_key="YOUR_API_KEY")
```

If you need to set or update the API key after initializing the SDK, you can use:

```python
sdk.set_api_key("YOUR_API_KEY")
```

## Transcription Engines
The SDK supports two transcription modes: `Complete` and `Lite`. The desired mode can be specified via the `engine` parameter of the `transcribe` method. When omitted it defaults to `Complete`. 

When using the `Lite` engine, the request object has to specify explicit defaults for a few of the properties:

```python
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

            # Adding required parameters with null/empty values
            summarize=0,
            custom_vocabulary="",
            llm_translation=[],
            srt_translation=[],
        ),
        metadata={"test_id": "integration_test", "environment": "testing"},
    )
```

## Sample Usage

### The *source* parameter
All transcription methods of the `SaladCloudTranscriptionSdk` take a source parameter - the input file for the transcription job. 

The `source` can be a path pointing to a local file, like `/usr/share/my_video_project.mp4`. Or, it can be an URL, like `https://myserver.net/files/my_video_project.mp4`. 

When a local file is specified, the SDK will take care to upload that to the Saldad Simple Storage Service (S4) behind the scenes. When the upload is completed, the transcription job is run using as input an S4 URL.

When a remote file is specified, that URL is passed as-is to the transcription engine. Make sure the file is publicly accessible.  

### Start a Transcription Job and wait for it to complete

```python
from salad_cloud_transcription import SaladCloudTranscriptionSdk
from salad_cloud_transcription_sdk.models.transcription_engine import TranscriptionEngine
from salad_cloud_transcription_sdk.models.transcription_request import TranscriptionRequest
from salad_cloud_transcription_sdk.models.transcription_job_input import TranscriptionJobInput

# Initialize the SDK
sdk = SaladCloudTranscriptionSdk(api_key="your_api_key")

# Setup the request
request_object = TranscriptionRequest(
    options=TranscriptionJobInput(
        language_code="en",
        return_as_file=False,
        sentence_level_timestamps=True,
        word_level_timestamps=True,
        diarization=True,
        srt=True
    ),
    metadata={"project": "example_project"}
)

# Start a transcription job and wait for the result
result = sdk.transcription_client.transcribe(
    source="path/to/audio.mp3",
    organization_name="your_organization_name",
    request=request_object,
    auto_poll=True
)

# Print the transcription job output
print(result.output)
```

### Start a Transcription Job and poll for status

```python
from salad_cloud_transcription import SaladCloudTranscriptionSdk

# Initialize the SDK
sdk = SaladCloudTranscriptionSdk(api_key="your_api_key")

# Setup the request
request_object = TranscriptionRequest(
    options=TranscriptionJobInput(
        language_code="en",
        return_as_file=False,
        sentence_level_timestamps=True,
        word_level_timestamps=True,
        diarization=True,
        srt=True
    ),
    metadata={"project": "example_project"}
)

# Start a transcription job. auto_poll = False
job = sdk.transcription_client.transcribe(
    source = "path/to/audio.mp3",
    request = request_object,
    auto_poll = False)

# Poll for the job status
while True:
    job = self.get_transcription_job(organization_name, job.id_)
    if job.status in [
        Status.SUCCEEDED.value,
        Status.FAILED.value,
        Status.CANCELLED.value,
        ]:
        break
    time.sleep(5)

if job.status == Status.SUCCEEDED.value:
    print(job.output)
```

### Start a Transcription Job and Get Updates via a Webhook

```python
from salad_cloud_transcription import SaladCloudTranscriptionSdk
from salad_cloud_transcription_sdk.models.transcription_request import TranscriptionRequest
from salad_cloud_transcription_sdk.models.transcription_job_input import TranscriptionJobInput

# Initialize the SDK
sdk = SaladCloudTranscriptionSdk(api_key="your_api_key")

# Setup the request
request_object = TranscriptionRequest(
    options=TranscriptionJobInput(
        language_code="en",
        return_as_file=False,
        sentence_level_timestamps=True,
        word_level_timestamps=True,
        diarization=True,
        srt=True
    ),
    metadata={"project": "example_project"}
)

# Start a transcription job with a webhook URL
job = sdk.transcription_client.transcribe(
    source="path/to/audio.mp3",
    request=request_object,
    webhook_url="https://your-webhook-endpoint.com"
)

print(f"Job started with ID: {job.id}")
```

In your webhook handler you need to validate the payload being sent to you:

```python
from salad_cloud_transcription import SaladCloudTranscriptionSdk

def webhook_handler(request):
    # Initialize the SDK
    sdk = SaladCloudTranscriptionSdk(api_key="your_api_key")

    # Extract the signing parameters from the request headers
    payload = request.json()  
    webhook_signature = request.headers.get("webhook-signature")
    webhook_timestamp = request.headers.get("webhook-timestamp")
    webhook_message_id = request.headers.get("webhook-id")
 
    # Retrieve the webhook signing secret for your Salad organization
    sdk = SaladCloudTranscriptionSdk(api_key="your_api_key")
    secret_key_service = sdk.webhook_secret_key
    secret_key_response = secret_key_service.get_webhook_secret_key(
        "your_organization_name")

    signing_secret = f"whsec_{secret_key_response.secret_key}"

    # Process the webhook payload
    var job = sdk.transcription_client.process_webhook_request(
        payload=payload,
        signing_secret = signing_secret,
        webhook_id=webhook_message_id,
        webhook_timestamp=webhook_timestamp,
        webhook_signature=webhook_signature,
    )

    # The payload verification result is a TranscriptionWebhookPayload. 
    # Its data field is a InferenceEndpointJob and it contains the transcription job output.
    print(job.data)
```

## License

This SDK is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please email support@salad.com or visit our documentation at https://docs.salad.com.
