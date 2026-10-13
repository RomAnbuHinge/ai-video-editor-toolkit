"""Auto-caption handler — VAD -> ASR backend -> timed subtitle track."""
from __future__ import annotations

from dataclasses import dataclass

from aive.models.registry import get_backend
from aive.services.audio_extract import extract_audio_track
from aive.utils.logging_setup import get_logger

log = get_logger("aive.handlers.auto_caption")


@dataclass
class Caption:
    start_s: float
    end_s: float
    text: str


def transcribe(source: str, language: str = "en") -> list[Caption]:
    """Extract the audio track, run the ASR backend, return timed captions."""
    wav_path = extract_audio_track(source, target_sr=16000)
    asr = get_backend("asr")
    segments = asr.transcribe(str(wav_path), language=language)
    caps = [Caption(start_s=s.start, end_s=s.end, text=s.text.strip())
            for s in segments if s.text.strip()]
    log.info("transcribe: %d caption segments (%s)", len(caps), language)
    return caps


def to_srt(captions: list[Caption]) -> str:
    def _ts(t: float) -> str:
        h, rem = divmod(t, 3600)
        m, s = divmod(rem, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"

    out: list[str] = []
    for i, c in enumerate(captions, start=1):
        out.append(f"{i}\n{_ts(c.start_s)} --> {_ts(c.end_s)}\n{c.text}\n")
    return "\n".join(out)