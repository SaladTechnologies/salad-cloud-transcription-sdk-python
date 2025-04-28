from __future__ import annotations
from typing import Dict, List, Any, Optional, Union
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel


class WordSegment(BaseModel):
    """A word segment in the transcription with timing and speaker information

    :param start: Start time of the word in seconds
    :type start: float
    :param end: End time of the word in seconds
    :type end: float
    :param timestamp: Timestamp as [start, end]
    :type timestamp: List[float]
    :param word: The transcribed word
    :type word: str
    :param speaker: The speaker identifier
    :type speaker: str
    """

    def __init__(
        self,
        start: float,
        end: float,
        timestamp: List[float],
        word: str,
        speaker: str,
        **kwargs,
    ):
        self.start = self._define_number("start", start)
        self.end = self._define_number("end", end)
        self.timestamp = timestamp
        self.word = self._define_str("word", word)
        self.speaker = self._define_str("speaker", speaker)
        self._kwargs = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Converts the WordSegment to a dictionary

        :return: Dictionary representation of this instance
        :rtype: Dict[str, Any]
        """
        return {
            "start": self.start,
            "end": self.end,
            "timestamp": self.timestamp,
            "word": self.word,
            "speaker": self.speaker,
        }


class SentenceTimestamp(BaseModel):
    """A sentence with timestamp information

    :param start: Start time of the sentence in seconds
    :type start: float
    :param end: End time of the sentence in seconds
    :type end: float
    :param timestamp: Timestamp as [start, end]
    :type timestamp: List[float]
    :param text: The transcribed sentence text
    :type text: str
    :param speaker: The speaker identifier (optional)
    :type speaker: Optional[str]
    """

    def __init__(
        self,
        start: float,
        end: float,
        timestamp: List[float],
        text: str,
        speaker: Optional[str] = None,
        **kwargs,
    ):
        self.start = self._define_number("start", start)
        self.end = self._define_number("end", end)
        self.timestamp = timestamp
        self.text = self._define_str("text", text)
        self.speaker = speaker
        self._kwargs = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Converts the SentenceTimestamp to a dictionary

        :return: Dictionary representation of this instance
        :rtype: Dict[str, Any]
        """
        result = {
            "start": self.start,
            "end": self.end,
            "timestamp": self.timestamp,
            "text": self.text,
        }

        if self.speaker is not None:
            result["speaker"] = self.speaker

        return result


@JsonMap({})
class TranscriptionJobOutput(BaseModel):
    """The output of a transcription job

    :param text: Complete transcribed text
    :type text: str
    :param word_segments: List of word segments with timing and speaker information
    :type word_segments: List[WordSegment]
    :param sentence_level_timestamps: List of sentences with timing and speaker information
    :type sentence_level_timestamps: List[SentenceTimestamp]
    :param srt_content: SRT formatted content for subtitles
    :type srt_content: str
    :param duration_in_seconds: Duration of the audio in seconds
    :type duration_in_seconds: float
    :param processing_time: Processing time in seconds
    :type processing_time: float
    :param summary: Summary of the transcription content (optional)
    :type summary: Optional[str]
    :param llm_translation: Translations of the transcription in different languages (optional)
    :type llm_translation: Optional[Dict[str, str]]
    :param srt_translation: Translations of the SRT content in different languages (optional)
    :type srt_translation: Optional[Dict[str, str]]
    :param duration: Duration in hours (optional)
    :type duration: Optional[float]
    :param overall_processing_time: Overall processing time in seconds (optional)
    :type overall_processing_time: Optional[float]
    """

    def __init__(
        self,
        text: str,
        word_segments: List[Dict[str, Any]],
        sentence_level_timestamps: List[Dict[str, Any]],
        srt_content: str,
        duration_in_seconds: float,
        processing_time: float,
        summary: Optional[str] = None,  # optional in Lite
        llm_translation: Optional[Dict[str, str]] = None,  # optional in Lite
        srt_translation: Optional[Dict[str, str]] = None,  # optional in Lite
        duration: Optional[float] = None,  # optional in Lite
        overall_processing_time: Optional[float] = None,  # optional in Lite
        **kwargs,
    ):
        self.text = self._define_str("text", text)
        self.word_segments = [WordSegment(**segment) for segment in word_segments]
        self.sentence_level_timestamps = [
            SentenceTimestamp(**sentence) for sentence in sentence_level_timestamps
        ]
        self.srt_content = self._define_str("srt_content", srt_content)
        self.summary = summary
        self.llm_translation = llm_translation
        self.srt_translation = srt_translation
        self.duration_in_seconds = self._define_number(
            "duration_in_seconds", duration_in_seconds
        )
        self.duration = self._define_number("duration", duration) if duration else None
        self.processing_time = self._define_number("processing_time", processing_time)
        self.overall_processing_time = (
            self._define_number("overall_processing_time", overall_processing_time)
            if overall_processing_time
            else None
        )
        self._kwargs = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Converts the TranscriptionJobOutput to a dictionary

        :return: Dictionary representation of this instance
        :rtype: Dict[str, Any]
        """
        result = {
            "text": self.text,
            "word_segments": [segment.to_dict() for segment in self.word_segments],
            "sentence_level_timestamps": [
                sentence.to_dict() for sentence in self.sentence_level_timestamps
            ],
            "srt_content": self.srt_content,
            "duration_in_seconds": self.duration_in_seconds,
            "processing_time": self.processing_time,
        }

        # Add optional fields if they exist
        if self.summary is not None:
            result["summary"] = self.summary
        if self.llm_translation is not None:
            result["llm_translation"] = self.llm_translation
        if self.srt_translation is not None:
            result["srt_translation"] = self.srt_translation
        if self.duration is not None:
            result["duration"] = self.duration
        if self.overall_processing_time is not None:
            result["overall_processing_time"] = self.overall_processing_time

        return result

    @classmethod
    def from_json(
        cls, json_data: Union[str, bytes, Dict[str, Any]]
    ) -> TranscriptionJobOutput:
        """Creates a TranscriptionJobOutput instance from JSON data

        :param json_data: JSON string, bytes, or dictionary representation of TranscriptionJobOutput
        :type json_data: Union[str, bytes, Dict[str, Any]]
        :return: A new TranscriptionJobOutput instance
        :rtype: TranscriptionJobOutput
        """
        import json

        if isinstance(json_data, dict):
            data = json_data
        else:
            if isinstance(json_data, bytes):
                json_data = json_data.decode("utf-8")
            data = json.loads(json_data)

        return cls(**data)
