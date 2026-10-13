"""Backend registry. Loads available inference backends lazily and caches."""
from __future__ import annotations

from typing import Protocol

from aive.config.settings import Settings
from aive.utils.logging_setup import get_logger

log = get_logger("aive.models.registry")


class InferenceBackend(Protocol):
    name: str

    def warmup(self) -> None: ...
    def infer(self, *args, **kwargs): ...
    def transcribe(self, path: str, *, language: str = "en"): ...


_BACKENDS: dict[str, InferenceBackend] = {}
_SETTINGS: Settings | None = None


def load_backends(settings: Settings) -> None:
    global _SETTINGS
    _SETTINGS = settings
    log.info("backend device=%s weights_dir=%s",
             settings.models.device, settings.models.weights_dir)
    # Real backends are registered here on demand; registry stays lazy so the
    # UI can boot without loading every model.


def register(name: str, backend: InferenceBackend) -> None:
    _BACKENDS[name] = backend
    log.info("registered backend: %s", name)


def get_backend(name: str) -> InferenceBackend:
    if name not in _BACKENDS:
        raise KeyError(f"backend {name!r} not loaded; call load_backends() first")
    return _BACKENDS[name]