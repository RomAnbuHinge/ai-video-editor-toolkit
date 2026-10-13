"""Threaded render queue. One worker per job, bounded concurrency."""
from __future__ import annotations

import queue
import threading
from dataclasses import dataclass, field
from typing import Callable

from aive.utils.logging_setup import get_logger

log = get_logger("aive.core.render_queue")


@dataclass
class RenderJob:
    job_id: str
    run: Callable[[], None]
    label: str = ""
    done: threading.Event = field(default_factory=threading.Event)


class RenderQueue:
    def __init__(self, max_concurrent: int = 1) -> None:
        self._q: queue.Queue[RenderJob | None] = queue.Queue()
        self._workers: list[threading.Thread] = []
        self._max = max_concurrent
        self._running = False

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        for i in range(self._max):
            t = threading.Thread(target=self._loop, name=f"render-{i}", daemon=True)
            t.start()
            self._workers.append(t)
        log.info("render queue started (%d workers)", self._max)

    def stop(self) -> None:
        if not self._running:
            return
        for _ in self._workers:
            self._q.put(None)
        for t in self._workers:
            t.join(timeout=5.0)
        self._workers.clear()
        self._running = False
        log.info("render queue stopped")

    def submit(self, job: RenderJob) -> None:
        self._q.put(job)

    def drain(self) -> None:
        self._q.join()

    def _loop(self) -> None:
        while True:
            job = self._q.get()
            try:
                if job is None:
                    return
                log.info("render job start: %s", job.label or job.job_id)
                job.run()
                job.done.set()
                log.info("render job done: %s", job.label or job.job_id)
            except Exception:
                log.exception("render job failed: %s", getattr(job, "job_id", "?"))
            finally:
                self._q.task_done()