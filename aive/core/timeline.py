"""Timeline model + project (.aiveproj) load/save."""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable

from aive.utils.logging_setup import get_logger

log = get_logger("aive.core.timeline")

PROJECT_SCHEMA = "aive.project/2"


@dataclass
class Clip:
    clip_id: str
    source: str
    in_s: float
    out_s: float
    label: str = ""


@dataclass
class Timeline:
    clips: list[Clip] = field(default_factory=list)
    _subscribers: list[Callable[["Timeline"], None]] = field(default_factory=list, repr=False)

    @classmethod
    def empty(cls) -> "Timeline":
        return cls()

    def subscribe(self, cb: Callable[["Timeline"], None]) -> None:
        self._subscribers.append(cb)

    def _notify(self) -> None:
        for cb in list(self._subscribers):
            try:
                cb(self)
            except Exception:  # a bad UI subscriber must not kill the engine
                log.exception("timeline subscriber raised")

    def add_clip(self, source: str, in_s: float, out_s: float, label: str = "") -> Clip:
        if out_s <= in_s:
            raise ValueError(f"out_s ({out_s}) must exceed in_s ({in_s})")
        clip = Clip(clip_id=uuid.uuid4().hex[:12], source=source,
                    in_s=in_s, out_s=out_s, label=label)
        self.clips.append(clip)
        self._notify()
        return clip

    def total_duration(self) -> float:
        return sum(c.out_s - c.in_s for c in self.clips)


def load_project(path: Path) -> Timeline:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != PROJECT_SCHEMA:
        log.warning("project schema %r != %r; attempting best-effort load",
                    data.get("schema"), PROJECT_SCHEMA)
    tl = Timeline()
    for raw in data.get("clips", []):
        tl.clips.append(Clip(**raw))
    return tl


def save_project(timeline: Timeline, path: Path) -> None:
    payload = {"schema": PROJECT_SCHEMA, "clips": [asdict(c) for c in timeline.clips]}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    log.info("saved project: %s (%d clips)", path, len(timeline.clips))