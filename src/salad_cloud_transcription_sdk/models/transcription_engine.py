from enum import Enum


class TranscriptionEngine(Enum):
    """
    Enum representing the different transcription engine options.

    Options:
        - Complete: Complete transcription engine which siupports all features
        - Lite: Lightweight transcription engine with less features, aimed at being faster
    """

    Complete = "complete"
    Lite = "lite"
