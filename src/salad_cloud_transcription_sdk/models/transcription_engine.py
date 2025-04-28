from enum import Enum


class TranscriptionEngine(Enum):
    """
    Enum representing the different transcription engine options.

    Options:
        - Full: Full transcription engine which supports all features
        - Lite: Lightweight transcription engine with less features, aimed at being faster
    """

    Full = "full"
    Lite = "lite"
