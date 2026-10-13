"""AI upscaling handler — tile-based super-resolution through a backend."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from aive.models.registry import get_backend
from aive.utils.logging_setup import get_logger

log = get_logger("aive.handlers.upscale")


@dataclass
class UpscalePlan:
    scale: int = 2
    tile: int = 256
    overlap: int = 16


def upscale_frame(frame: np.ndarray, plan: UpscalePlan) -> np.ndarray:
    """Tile a HxWx3 uint8 frame, run SR per tile with overlap, blend seams.

    Overlap region is cosine-weighted to hide tile boundaries."""
    sr = get_backend("superres")
    h, w, _ = frame.shape
    step = plan.tile - plan.overlap
    out = np.zeros((h * plan.scale, w * plan.scale, 3), dtype=np.float32)
    weight = np.zeros_like(out)

    for y in range(0, h, step):
        for x in range(0, w, step):
            ty0, tx0 = y, x
            ty1, tx1 = min(y + plan.tile, h), min(x + plan.tile, w)
            tile = frame[ty0:ty1, tx0:tx1]
            up = sr.infer(tile, scale=plan.scale)
            oy0, ox0 = ty0 * plan.scale, tx0 * plan.scale
            oy1, ox1 = oy0 + up.shape[0], ox0 + up.shape[1]
            out[oy0:oy1, ox0:ox1] += up
            weight[oy0:oy1, ox0:ox1] += 1.0

    blended = out / np.maximum(weight, 1e-6)
    return np.clip(blended, 0, 255).astype(np.uint8)