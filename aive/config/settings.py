"""Typed settings loaded from config.toml with sane Windows defaults."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib  # py3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

from aive.utils.paths import default_config_dir, default_cache_dir


@dataclass(frozen=True)
class LoggingSettings:
    level: str = "INFO"
    file: str = "logs/aive.log"
    rotate_mb: int = 8
    keep: int = 5


@dataclass(frozen=True)
class PipelineSettings:
    isolate_decoder: bool = True
    decoder_workers: int = 2
    ring_buffer_frames: int = 96
    scene_threshold: float = 0.42
    proxy_height: int = 540


@dataclass(frozen=True)
class ModelSettings:
    backend: str = "onnxruntime"
    device: str = "auto"           # auto | cpu | cuda | dml
    weights_dir: str = "models/weights"
    allow_pickle: bool = False
    max_vram_mb: int = 6144


@dataclass(frozen=True)
class RenderSettings:
    encoder: str = "auto"          # auto | nvenc | qsv | amf | libx264
    crf: int = 19
    preset: str = "slow"
    threads: int = 0               # 0 -> let ffmpeg decide


@dataclass(frozen=True)
class Settings:
    profile: str = "desktop"
    config_dir: Path = field(default_factory=default_config_dir)
    cache_dir: Path = field(default_factory=default_cache_dir)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    pipeline: PipelineSettings = field(default_factory=PipelineSettings)
    models: ModelSettings = field(default_factory=ModelSettings)
    render: RenderSettings = field(default_factory=RenderSettings)


def _merge(dc_type, raw: dict[str, Any]):
    known = {f for f in dc_type.__dataclass_fields__}  # type: ignore[attr-defined]
    filtered = {k: v for k, v in raw.items() if k in known}
    return dc_type(**filtered)  # type: ignore[call-arg]


def load_settings(config_path: str | None = None) -> Settings:
    """Load settings from config.toml (explicit path, else default dir)."""
    path = Path(config_path) if config_path else default_config_dir() / "config.toml"
    raw: dict[str, Any] = {}
    if path.is_file():
        with path.open("rb") as fh:
            raw = tomllib.load(fh)

    profile = os.environ.get("AIVE_PROFILE", raw.get("profile", "desktop"))
    return Settings(
        profile=profile,
        logging=_merge(LoggingSettings, raw.get("logging", {})),
        pipeline=_merge(PipelineSettings, raw.get("pipeline", {})),
        models=_merge(ModelSettings, raw.get("models", {})),
        render=_merge(RenderSettings, raw.get("render", {})),
    )