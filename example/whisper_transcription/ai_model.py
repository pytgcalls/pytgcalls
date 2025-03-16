import struct
from io import BytesIO
from typing import Optional

import numpy as np
from faster_whisper import WhisperModel

from pytgcalls.types import AudioQuality


class AIModel:
    def __init__(
        self,
        quality: AudioQuality,
        model_size: str = 'base',
        silence_threshold: float = 0.01,
        silence_duration: int = 2,
        use_context: bool = True,
        condition_on_prev_text: bool = False,
        multilingual: bool = True,
        language: Optional[str] = None,
    ):
        try:
            torch = __import__('torch')
            use_cuda = torch.cuda.is_available()
        except ImportError:
            use_cuda = False

        if use_cuda:
            self._model = WhisperModel(
                model_size,
                device='cuda',
                compute_type='float16',
            )
        else:
            self._model = WhisperModel(
                model_size,
                device='cpu',
                compute_type='int8',
            )
        self._sample_rate = quality.value[0]
        self._channels = quality.value[1]
        self._temp_file = BytesIO()
        self._silent_frames = 0
        self._not_transcribed = False
        self._current_context = ''
        self._silence_threshold = silence_threshold
        self._silence_duration = silence_duration
        self._use_context = use_context
        self._condition_on_prev_text = condition_on_prev_text
        self._multilingual = multilingual
        self._language = language

    def _is_silent(
        self,
        data: bytes,
    ) -> bool:
        buffer = np.frombuffer(data, dtype=np.int16)
        if self._channels > 1:
            buffer = buffer.reshape(-1, self._channels).mean(axis=1)
        buffer = buffer.astype(np.float32) / np.iinfo(np.int16).max
        rms = np.sqrt(np.mean(np.square(buffer)))
        return rms < self._silence_threshold

    def _to_wav(self, data: bytes) -> bytes:
        byte_rate = self._sample_rate * self._channels * 2
        block_align = self._channels * 2
        sub_chunk2_size = len(data)
        chunk_size = 36 + sub_chunk2_size
        wav_header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',
            chunk_size,
            b'WAVE',
            b'fmt ',
            16,
            1,
            self._channels,
            self._sample_rate,
            byte_rate,
            block_align,
            16,
            b'data',
            sub_chunk2_size,
        )
        return wav_header + data

    def transcribe(self, data: bytes) -> Optional[str]:
        if self._is_silent(data):
            self._silent_frames += len(data)
        else:
            self._silent_frames = 0
            self._not_transcribed = True
        self._temp_file.write(data)
        silence_threshold = (
            self._sample_rate * self._channels *
            2 * self._silence_duration
        )
        if self._silent_frames >= silence_threshold and \
                self._not_transcribed:
            self._not_transcribed = False
            self._silent_frames = 0
            self._temp_file.seek(0)
            pcm_data = self._temp_file.getvalue()
            self._temp_file.seek(0)
            self._temp_file.truncate()
            return self._internal_transcribe(pcm_data)
        return None

    def _internal_transcribe(self, data: bytes) -> Optional[str]:
        wav_file = BytesIO()
        wav_file.write(self._to_wav(data))
        wav_file.seek(0)
        segments, info = self._model.transcribe(
            wav_file,
            vad_filter=True,
            language=self._language,
            initial_prompt=self._current_context
            if self._use_context else None,
            condition_on_previous_text=self._condition_on_prev_text,
            multilingual=self._multilingual,
        )
        if info.duration_after_vad < 1:
            return None
        message = ''
        for segment in segments:
            txt = segment.text.lstrip(' ')
            message += txt + ' '
            if self._use_context:
                self._current_context += txt + ' '
        return message.lstrip(' ')
