"""Logging setup. Rotating file handler + rich console."""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from aive.config.settings import LoggingSettings

_CONFIGURED = False


def configure_logging(settings: LoggingSettings, override_level: str | None = None) -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    level = (override_level or settings.level).upper()
    root = logging.getLogger("aive")
    root.setLevel(level)

    Path(settings.file).parent.mkdir(parents=True, exist_ok=True)
    fh = RotatingFileHandler(settings.file, maxBytes=settings.rotate_mb * 1024 * 1024,
                             backupCount=settings.keep, encoding="utf-8")
    fh.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s: %(message)s"))
    root.addHandler(fh)

    try:
        from rich.logging import RichHandler
        ch = RichHandler(rich_tracebacks=True, show_path=False)
        ch.setFormatter(logging.Formatter("%(message)s"))
    except ImportError:  # pragma: no cover
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    root.addHandler(ch)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)