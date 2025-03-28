from __future__ import annotations
from enum import Enum
from typing import List, Union, Dict, Any
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL


class TranslationLanguage(Enum):
    GERMAN = "german"
    ITALIAN = "italian"
    FRENCH = "french"
    SPANISH = "spanish"
    ENGLISH = "english"
    PORTUGUESE = "portuguese"
    HINDI = "hindi"
    THAI = "thai"
    
    @classmethod
    def list(cls):
        return list(cls)


@JsonMap({})
class TranscriptionJobInput(BaseModel):
    """Configuration for a transcription job
    
    :param return_as_file: Set to "true" to receive the transcription output as a downloadable file URL, especially useful for large responses. Set to "false" (default) to receive the full transcription in the API response. If the response exceeds 1 MB in size, it will automatically be returned as a link to a file, regardless of the return_as_file setting.
    :type return_as_file: bool
    :param language_code: Transcription is available in 97 languages. We automatically identify the source language. In order to make diarization more accurate, please provide your transcription language.
    :type language_code: str
    :param translate: We are excited to announce that we've added translation to English to our service. To enable translation, you need to specify the following parameter: "translate": "to_eng". When using translation, you can still add other features such as SRT generation, timestamps, and diarization. Note that if you use translation, the original transcription is not returned. Translation is currently available for translation from single language to English only.
    :type translate: str
    :param sentence_level_timestamps: Sentence level timestamps are returned on default. Set to false if not needed.
    :type sentence_level_timestamps: bool
    :param word_level_timestamps: Set to "true" for word level timestamps. Set to "false" on default.
    :type word_level_timestamps: bool
    :param diarization: Set to "true" for speaker separation and identification. Set to "false" on default. Diarization requires the language_code to be defined. By default, it is set to "en" (English). Supports multiple languages including French, German, Spanish, Italian, Japanese, Chinese, and more.
    :type diarization: bool
    :param sentence_diarization: Set to "true" to return speaker information at the sentence level. If several speakers are identified in one sentence, the most prominent one will be returned. Set to "false" by default.
    :type sentence_diarization: bool
    :param srt: Set to "true" to generate a .srt output for caption and subtitles. Set to "false" on default.
    :type srt: bool
    :param summarize: Set to a positive integer to receive a summary of the transcription in the specified number of words or less. For example, "summarize": 100 will provide a summary of up to 100 words. Set to 0 (default) if summarization is not needed.
    :type summarize: int
    :param llm_translation: Leverage our new LLM integration to translate the transcription in between multiple languages. Supported languages for LLM translation are: English, French, German, Italian, Portuguese, Hindi, Spanish, and Thai.
    :type llm_translation: List[TranslationLanguage]
    :param srt_translation: Use our LLM integration to translate the generated SRT captions into multiple languages. Same languages are supported as for llm_translation.
    :type srt_translation: List[TranslationLanguage]
    :param custom_vocabulary: Provide a comma-separated list of terms or phrases that are specific to your transcription context. This helps improve transcription accuracy for domain-specific terminology. (in preview)
    :type custom_vocabulary: str
    """

    def __init__(
        self,
        return_as_file: bool,
        language_code: str,
        translate: str,
        sentence_level_timestamps: bool,
        word_level_timestamps: bool,
        diarization: bool,
        sentence_diarization: bool,
        srt: bool,
        summarize: int,
        llm_translation: List[TranslationLanguage],
        srt_translation: List[TranslationLanguage],
        custom_vocabulary: str,
        **kwargs,
    ):
        self.return_as_file = return_as_file
        self.language_code = self._define_str("language_code", language_code)
        self.translate = self._define_str("translate", translate)
        self.sentence_level_timestamps = sentence_level_timestamps
        self.word_level_timestamps = word_level_timestamps
        self.diarization = diarization
        self.sentence_diarization = sentence_diarization
        self.srt = srt
        self.summarize = self._define_number("summarize", summarize, ge=0)
        self.llm_translation = self._define_list(llm_translation, TranslationLanguage)
        self.srt_translation = self._define_list(srt_translation, TranslationLanguage)
        self.custom_vocabulary = self._define_str("custom_vocabulary", custom_vocabulary)
        self._kwargs = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Converts the TranscriptionJobInput object to a dictionary
        
        :return: Dictionary representation of this instance
        :rtype: Dict[str, Any]
        """
        result = {
            "return_as_file": self.return_as_file,
            "language_code": self.language_code,
            "translate": self.translate,
            "sentence_level_timestamps": self.sentence_level_timestamps,
            "word_level_timestamps": self.word_level_timestamps,
            "diarization": self.diarization,
            "sentence_diarization": self.sentence_diarization,
            "srt": self.srt,
            "summarize": self.summarize,
            "custom_vocabulary": self.custom_vocabulary,
        }
        
        if self.llm_translation:
            result['llm_translation'] = ", ".join(lang.value for lang in self.llm_translation)
        if self.srt_translation:
            result['srt_translation'] = ", ".join(lang.value for lang in self.srt_translation)
        
        return result

