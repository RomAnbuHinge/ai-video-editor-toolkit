"""EditorEngine — owns the timeline, the decode pipeline, and render jobs."""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from aive.config.settings import Settings
from aive.core.timeline import Timeline, load_project, save_project
from aive.core.render_queue import RenderQueue
from aive.services.decoder import DecoderService
from aive.models.registry import load_backends
from aive.utils.logging_setup import get_logger

log = get_logger("aive.core.engine")


@dataclass
class EditorEngine:
    settings: Settings
    timeline: Timeline = field(default_factory=Timeline.empty)
    render_queue: RenderQueue = field(default_factory=RenderQueue)
    _decoder: DecoderService | None = None
    _started: bool = False
    _lock: threading.RLock = field(default_factory=threading.RLock)

    def start(self) -> None:
        with self._lock:
            if self._started:
                return
            log.info("engine start: decoder_workers=%d", self.settings.pipeline.decoder_workers)
            self._decoder = DecoderService(self.settings)
            load_backends(self.settings)
            self.render_queue.start()
            self._started = True

    def shutdown(self) -> None:
        with self._lock:
            if not self._started:
                return
            self.render_queue.stop()
            if self._decoder:
                self._decoder.close()
            self._started = False
            log.info("engine shutdown clean")

    def open_project(self, path: str | Path) -> None:
        self.timeline = load_project(Path(path))

    def save_project(self, path: str | Path) -> None:
        save_project(self.timeline, Path(path))

    def run_headless(self) -> None:
        log.info("headless run: %d clips", len(self.timeline.clips))
        self.render_queue.drain()

    def on_timeline_change(self, cb: Callable[[Timeline], None]) -> None:
        self.timeline.subscribe(cb)