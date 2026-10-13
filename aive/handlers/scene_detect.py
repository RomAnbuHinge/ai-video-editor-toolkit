"""Scene-change detection handler over decoded frame stream."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from aive.core.timeline import Timeline
from aive.services.decoder import DecoderService, Frame
from aive.utils.logging_setup import get_logger

log = get_logger("aive.handlers.scene_detect")


@dataclass
class SceneBoundary:
    t_s: float
    score: float


def _histogram_diff(a: np.ndarray, b: np.ndarray) -> float:
    """Chi-square distance between normalized luma histograms, in [0, 1]."""
    ha, _ = np.histogram(a, bins=64, range=(0, 256), density=True)
    hb, _ = np.histogram(b, bins=64, range=(0, 256), density=True)
    ha = ha + 1e-9
    hb = hb + 1e-9
    chi = 0.5 * np.sum(((ha - hb) ** 2) / (ha + hb))
    return float(min(1.0, chi))


def detect_scenes(decoder: DecoderService, source: str,
                  threshold: float = 0.42) -> list[SceneBoundary]:
    """Return scene boundaries where consecutive-frame histogram distance
    exceeds `threshold`. O(frames * bins)."""
    boundaries: list[SceneBoundary] = []
    prev: np.ndarray | None = None
    for frame in decoder.iter_frames(source):
        if prev is not None:
            score = _histogram_diff(prev, frame.luma)
            if score >= threshold:
                boundaries.append(SceneBoundary(t_s=frame.t_s, score=score))
        prev = frame.luma
    log.info("scene detect: %d boundaries (threshold=%.2f)", len(boundaries), threshold)
    return boundaries


def apply_to_timeline(timeline: Timeline, boundaries: list[SceneBoundary],
                      source: str) -> None:
    for i in range(len(boundaries) - 1):
        timeline.add_clip(source, boundaries[i].t_s, boundaries[i + 1].t_s,
                          label=f"scene-{i:03d}")
    log.info("timeline got %d scene clips", max(0, len(boundaries) - 1))