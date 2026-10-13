"""Extract a mono PCM track for ASR from any container ffmpeg understands."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from aive.utils.logging_setup import get_logger

log = get_logger("aive.services.audio_extract")


def extract_audio_track(source: str, target_sr: int = 16000) -> Path:
    """Return a temp .wav path with mono PCM at `target_sr`.

    Uses the system ffmpeg. Raises RuntimeError if ffmpeg is missing or fails."""
    out = Path(tempfile.mkstemp(suffix=".wav", prefix="aive_audio_")[1])
    cmd = [
        "ffmpeg", "-y", "-i", source,
        "-vn", "-ac", "1", "-ar", str(target_sr),
        "-f", "wav", str(out),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    except FileNotFoundError as exc:
        raise RuntimeError("ffmpeg not found on PATH") from exc
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr[-400:]}")
    log.info("extracted audio -> %s", out)
    return out