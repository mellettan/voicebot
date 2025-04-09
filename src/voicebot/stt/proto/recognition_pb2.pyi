from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EouReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED: _ClassVar[EouReason]
    ORGANIC: _ClassVar[EouReason]
    NO_SPEECH_TIMEOUT: _ClassVar[EouReason]
    MAX_SPEECH_TIMEOUT: _ClassVar[EouReason]
UNSPECIFIED: EouReason
ORGANIC: EouReason
NO_SPEECH_TIMEOUT: EouReason
MAX_SPEECH_TIMEOUT: EouReason

class RecognitionRequest(_message.Message):
    __slots__ = ("options", "audio_chunk")
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    AUDIO_CHUNK_FIELD_NUMBER: _ClassVar[int]
    options: RecognitionOptions
    audio_chunk: bytes
    def __init__(self, options: _Optional[_Union[RecognitionOptions, _Mapping]] = ..., audio_chunk: _Optional[bytes] = ...) -> None: ...

class RecognitionResponse(_message.Message):
    __slots__ = ("transcription", "backend_info", "insight", "vad")
    TRANSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    BACKEND_INFO_FIELD_NUMBER: _ClassVar[int]
    INSIGHT_FIELD_NUMBER: _ClassVar[int]
    VAD_FIELD_NUMBER: _ClassVar[int]
    transcription: Transcription
    backend_info: BackendInfo
    insight: InsightResult
    vad: VADResult
    def __init__(self, transcription: _Optional[_Union[Transcription, _Mapping]] = ..., backend_info: _Optional[_Union[BackendInfo, _Mapping]] = ..., insight: _Optional[_Union[InsightResult, _Mapping]] = ..., vad: _Optional[_Union[VADResult, _Mapping]] = ...) -> None: ...

class Transcription(_message.Message):
    __slots__ = ("channel", "results", "eou", "eou_reason", "processed_audio_start", "processed_audio_end", "emotions_result", "speaker_info")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    EOU_FIELD_NUMBER: _ClassVar[int]
    EOU_REASON_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_AUDIO_START_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_AUDIO_END_FIELD_NUMBER: _ClassVar[int]
    EMOTIONS_RESULT_FIELD_NUMBER: _ClassVar[int]
    SPEAKER_INFO_FIELD_NUMBER: _ClassVar[int]
    channel: int
    results: _containers.RepeatedCompositeFieldContainer[Hypothesis]
    eou: bool
    eou_reason: EouReason
    processed_audio_start: _duration_pb2.Duration
    processed_audio_end: _duration_pb2.Duration
    emotions_result: Emotions
    speaker_info: SpeakerInfo
    def __init__(self, channel: _Optional[int] = ..., results: _Optional[_Iterable[_Union[Hypothesis, _Mapping]]] = ..., eou: bool = ..., eou_reason: _Optional[_Union[EouReason, str]] = ..., processed_audio_start: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., processed_audio_end: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., emotions_result: _Optional[_Union[Emotions, _Mapping]] = ..., speaker_info: _Optional[_Union[SpeakerInfo, _Mapping]] = ...) -> None: ...

class InsightResult(_message.Message):
    __slots__ = ("insight_result",)
    INSIGHT_RESULT_FIELD_NUMBER: _ClassVar[int]
    insight_result: str
    def __init__(self, insight_result: _Optional[str] = ...) -> None: ...

class VADResult(_message.Message):
    __slots__ = ("channel", "processed_audio_time", "utterance_detection_time")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_AUDIO_TIME_FIELD_NUMBER: _ClassVar[int]
    UTTERANCE_DETECTION_TIME_FIELD_NUMBER: _ClassVar[int]
    channel: int
    processed_audio_time: _duration_pb2.Duration
    utterance_detection_time: _duration_pb2.Duration
    def __init__(self, channel: _Optional[int] = ..., processed_audio_time: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., utterance_detection_time: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class OptionalBool(_message.Message):
    __slots__ = ("enable",)
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    def __init__(self, enable: bool = ...) -> None: ...

class RecognitionOptions(_message.Message):
    __slots__ = ("audio_encoding", "sample_rate", "channels_count", "language", "model", "enable_multi_utterance", "enable_partial_results", "hypotheses_count", "no_speech_timeout", "max_speech_timeout", "hints", "speaker_separation_options", "normalization_options", "insight_models", "enable_vad", "custom_ws_flow_control", "enable_long_utterances")
    class AudioEncoding(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AUDIO_ENCODING_UNSPECIFIED: _ClassVar[RecognitionOptions.AudioEncoding]
        PCM_S16LE: _ClassVar[RecognitionOptions.AudioEncoding]
        OPUS: _ClassVar[RecognitionOptions.AudioEncoding]
        MP3: _ClassVar[RecognitionOptions.AudioEncoding]
        FLAC: _ClassVar[RecognitionOptions.AudioEncoding]
        ALAW: _ClassVar[RecognitionOptions.AudioEncoding]
        MULAW: _ClassVar[RecognitionOptions.AudioEncoding]
        G729: _ClassVar[RecognitionOptions.AudioEncoding]
    AUDIO_ENCODING_UNSPECIFIED: RecognitionOptions.AudioEncoding
    PCM_S16LE: RecognitionOptions.AudioEncoding
    OPUS: RecognitionOptions.AudioEncoding
    MP3: RecognitionOptions.AudioEncoding
    FLAC: RecognitionOptions.AudioEncoding
    ALAW: RecognitionOptions.AudioEncoding
    MULAW: RecognitionOptions.AudioEncoding
    G729: RecognitionOptions.AudioEncoding
    AUDIO_ENCODING_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_COUNT_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    ENABLE_MULTI_UTTERANCE_FIELD_NUMBER: _ClassVar[int]
    ENABLE_PARTIAL_RESULTS_FIELD_NUMBER: _ClassVar[int]
    HYPOTHESES_COUNT_FIELD_NUMBER: _ClassVar[int]
    NO_SPEECH_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    MAX_SPEECH_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    HINTS_FIELD_NUMBER: _ClassVar[int]
    SPEAKER_SEPARATION_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    NORMALIZATION_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    INSIGHT_MODELS_FIELD_NUMBER: _ClassVar[int]
    ENABLE_VAD_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_WS_FLOW_CONTROL_FIELD_NUMBER: _ClassVar[int]
    ENABLE_LONG_UTTERANCES_FIELD_NUMBER: _ClassVar[int]
    audio_encoding: RecognitionOptions.AudioEncoding
    sample_rate: int
    channels_count: int
    language: str
    model: str
    enable_multi_utterance: OptionalBool
    enable_partial_results: OptionalBool
    hypotheses_count: int
    no_speech_timeout: _duration_pb2.Duration
    max_speech_timeout: _duration_pb2.Duration
    hints: Hints
    speaker_separation_options: SpeakerSeparationOptions
    normalization_options: NormalizationOptions
    insight_models: _containers.RepeatedScalarFieldContainer[str]
    enable_vad: OptionalBool
    custom_ws_flow_control: OptionalBool
    enable_long_utterances: OptionalBool
    def __init__(self, audio_encoding: _Optional[_Union[RecognitionOptions.AudioEncoding, str]] = ..., sample_rate: _Optional[int] = ..., channels_count: _Optional[int] = ..., language: _Optional[str] = ..., model: _Optional[str] = ..., enable_multi_utterance: _Optional[_Union[OptionalBool, _Mapping]] = ..., enable_partial_results: _Optional[_Union[OptionalBool, _Mapping]] = ..., hypotheses_count: _Optional[int] = ..., no_speech_timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., max_speech_timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., hints: _Optional[_Union[Hints, _Mapping]] = ..., speaker_separation_options: _Optional[_Union[SpeakerSeparationOptions, _Mapping]] = ..., normalization_options: _Optional[_Union[NormalizationOptions, _Mapping]] = ..., insight_models: _Optional[_Iterable[str]] = ..., enable_vad: _Optional[_Union[OptionalBool, _Mapping]] = ..., custom_ws_flow_control: _Optional[_Union[OptionalBool, _Mapping]] = ..., enable_long_utterances: _Optional[_Union[OptionalBool, _Mapping]] = ...) -> None: ...

class NormalizationOptions(_message.Message):
    __slots__ = ("enable", "profanity_filter", "punctuation", "capitalization", "question", "force_cyrillic")
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    PROFANITY_FILTER_FIELD_NUMBER: _ClassVar[int]
    PUNCTUATION_FIELD_NUMBER: _ClassVar[int]
    CAPITALIZATION_FIELD_NUMBER: _ClassVar[int]
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    FORCE_CYRILLIC_FIELD_NUMBER: _ClassVar[int]
    enable: OptionalBool
    profanity_filter: OptionalBool
    punctuation: OptionalBool
    capitalization: OptionalBool
    question: OptionalBool
    force_cyrillic: OptionalBool
    def __init__(self, enable: _Optional[_Union[OptionalBool, _Mapping]] = ..., profanity_filter: _Optional[_Union[OptionalBool, _Mapping]] = ..., punctuation: _Optional[_Union[OptionalBool, _Mapping]] = ..., capitalization: _Optional[_Union[OptionalBool, _Mapping]] = ..., question: _Optional[_Union[OptionalBool, _Mapping]] = ..., force_cyrillic: _Optional[_Union[OptionalBool, _Mapping]] = ...) -> None: ...

class Hints(_message.Message):
    __slots__ = ("words", "enable_letters", "eou_timeout")
    WORDS_FIELD_NUMBER: _ClassVar[int]
    ENABLE_LETTERS_FIELD_NUMBER: _ClassVar[int]
    EOU_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    words: _containers.RepeatedScalarFieldContainer[str]
    enable_letters: bool
    eou_timeout: _duration_pb2.Duration
    def __init__(self, words: _Optional[_Iterable[str]] = ..., enable_letters: bool = ..., eou_timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class SpeakerSeparationOptions(_message.Message):
    __slots__ = ("enable", "enable_only_main_speaker", "count")
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    ENABLE_ONLY_MAIN_SPEAKER_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    enable_only_main_speaker: bool
    count: int
    def __init__(self, enable: bool = ..., enable_only_main_speaker: bool = ..., count: _Optional[int] = ...) -> None: ...

class Hypothesis(_message.Message):
    __slots__ = ("text", "normalized_text", "start", "end", "word_alignments")
    class WordAlignment(_message.Message):
        __slots__ = ("word", "start", "end")
        WORD_FIELD_NUMBER: _ClassVar[int]
        START_FIELD_NUMBER: _ClassVar[int]
        END_FIELD_NUMBER: _ClassVar[int]
        word: str
        start: _duration_pb2.Duration
        end: _duration_pb2.Duration
        def __init__(self, word: _Optional[str] = ..., start: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., end: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    TEXT_FIELD_NUMBER: _ClassVar[int]
    NORMALIZED_TEXT_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    WORD_ALIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    text: str
    normalized_text: str
    start: _duration_pb2.Duration
    end: _duration_pb2.Duration
    word_alignments: _containers.RepeatedCompositeFieldContainer[Hypothesis.WordAlignment]
    def __init__(self, text: _Optional[str] = ..., normalized_text: _Optional[str] = ..., start: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., end: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., word_alignments: _Optional[_Iterable[_Union[Hypothesis.WordAlignment, _Mapping]]] = ...) -> None: ...

class Emotions(_message.Message):
    __slots__ = ("positive", "neutral", "negative", "positive_a", "neutral_a", "negative_a", "positive_t", "neutral_t", "negative_t")
    POSITIVE_FIELD_NUMBER: _ClassVar[int]
    NEUTRAL_FIELD_NUMBER: _ClassVar[int]
    NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    POSITIVE_A_FIELD_NUMBER: _ClassVar[int]
    NEUTRAL_A_FIELD_NUMBER: _ClassVar[int]
    NEGATIVE_A_FIELD_NUMBER: _ClassVar[int]
    POSITIVE_T_FIELD_NUMBER: _ClassVar[int]
    NEUTRAL_T_FIELD_NUMBER: _ClassVar[int]
    NEGATIVE_T_FIELD_NUMBER: _ClassVar[int]
    positive: float
    neutral: float
    negative: float
    positive_a: float
    neutral_a: float
    negative_a: float
    positive_t: float
    neutral_t: float
    negative_t: float
    def __init__(self, positive: _Optional[float] = ..., neutral: _Optional[float] = ..., negative: _Optional[float] = ..., positive_a: _Optional[float] = ..., neutral_a: _Optional[float] = ..., negative_a: _Optional[float] = ..., positive_t: _Optional[float] = ..., neutral_t: _Optional[float] = ..., negative_t: _Optional[float] = ...) -> None: ...

class BackendInfo(_message.Message):
    __slots__ = ("model_name", "model_version", "server_version")
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_VERSION_FIELD_NUMBER: _ClassVar[int]
    SERVER_VERSION_FIELD_NUMBER: _ClassVar[int]
    model_name: str
    model_version: str
    server_version: str
    def __init__(self, model_name: _Optional[str] = ..., model_version: _Optional[str] = ..., server_version: _Optional[str] = ...) -> None: ...

class SpeakerInfo(_message.Message):
    __slots__ = ("speaker_id", "main_speaker_confidence")
    SPEAKER_ID_FIELD_NUMBER: _ClassVar[int]
    MAIN_SPEAKER_CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    speaker_id: int
    main_speaker_confidence: float
    def __init__(self, speaker_id: _Optional[int] = ..., main_speaker_confidence: _Optional[float] = ...) -> None: ...
