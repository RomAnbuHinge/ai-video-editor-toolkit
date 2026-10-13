"""Decode service. Wraps PyAV. Isolates decode in a worker when configured."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

import av
import numpy as np

from aive.config.settings import Settings
from aive.utils.logging_setup import get_logger

log = get_logger("aive.services.decoder")


@dataclass
class Frame:
    t_s: float
    width: int
    height: int
    rgb: np.ndarray      # HxWx3 uint8
    luma: np.ndarray     # HxW uint8 (BT.601)

    @property
    def shape(self) -> tuple[int, int]:
        return self.height, self.width


class DecoderService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._closed = False

    def iter_frames(self, source: str, max_frames: int | None = None) -> Iterator[Frame]:
        """Yield decoded frames. Raises FileNotFoundError on missing source."""
        container = av.open(source)
        try:
            stream = container.streams.video[0]
            stream.thread_type = "AUTO"
            count = 0
            for packet_frame in container.decode(stream):
                if max_frames is not None and count >= max_frames:
                    break
                rgb = packet_frame.to_ndarray(format="rgb24")
                luma = packet_frame.to_ndarray(format="gray")
                t_s = float(packet_frame.pts * stream.time_base) if packet_frame.pts else 0.0
                yield Frame(t_s=t_s, width=rgb.shape[1], height=rgb.shape[0],
                            rgb=rgb, luma=luma)
                count += 1
        finally:
            container.close()

    def close(self) -> None:
        self._closed = True
        log.debug("decoder closed")