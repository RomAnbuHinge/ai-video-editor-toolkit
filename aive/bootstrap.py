"""Desktop entry point. Bootstrap -> config load -> engine start -> UI.

Run with:  python -m aive.bootstrap
"""
from __future__ import annotations

import sys
import argparse

from aive.config.settings import load_settings
from aive.utils.logging_setup import get_logger, configure_logging
from aive.core.engine import EditorEngine
from aive.ui.main_window import launch_ui


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="aive", description="AI video editor")
    parser.add_argument("--project", type=str, default=None, help="path to .aiveproj")
    parser.add_argument("--headless", action="store_true", help="run pipeline, no UI")
    parser.add_argument("--config", type=str, default=None, help="path to config.toml")
    parser.add_argument("--log-level", type=str, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    settings = load_settings(args.config)
    configure_logging(settings.logging, override_level=args.log_level)
    log = get_logger("aive.bootstrap")
    log.info("ai-video-editor-toolkit starting (profile=%s)", settings.profile)

    engine = EditorEngine(settings)
    try:
        engine.start()
        if args.project:
            engine.open_project(args.project)
        if args.headless:
            engine.run_headless()
            return 0
        return launch_ui(engine)
    finally:
        engine.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())