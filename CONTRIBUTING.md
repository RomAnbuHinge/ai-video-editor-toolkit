# Contributing to ai-video-editor-toolkit

Thanks for wanting to help build the AI video editor. This is a Windows-first
desktop toolkit for AI-assisted cutting, captioning, upscaling, and scene
assembly. Contributions that make the pipeline faster, the UI sharper, or the
model backends more portable are the ones we want most.

## Development setup

1. Install Python 3.11+ (3.12 recommended).
2. Create a venv: `py -3.12 -m venv .venv && .venv\Scripts\activate`.
3. Install dev deps: `pip install -r requirements.txt`.
4. Install the optional native accel layer: `pip install -e native/` (requires
   a C++17 toolchain + CMake 3.24+). This is optional — the pure-Python
   fallback path is always available.
5. Run the app: `python -m aive.bootstrap`.

## Branch & commit conventions

- Branch names: `feat/scene-detect-cuda`, `fix/ffmpeg-path-quoting`,
  `perf/decoder-ring-buffer`.
- Commit messages follow Conventional Commits: `feat(render): add NVENC
  fallback`, `fix(captions): handle RTL runs without crashing the layout`.
- Keep PRs scoped. One feature per PR. Rebase, don't merge from main.

## Code style

- `ruff` for lint + format. `ruff check . && ruff format .` before pushing.
- `mypy --strict` on `aive/core` and `aive/services`. Handlers may be looser.
- Type hints on every public function. No bare `except:`.
- Logging via `aive.utils.logging_setup.get_logger`, never `print` in shipped
  code paths.

## Tests

- `pytest -q` runs the unit suite.
- `pytest -m integration` runs the ffmpeg-backed integration suite (needs a
  real ffmpeg on PATH).
- New core logic needs a test. New model backends need a smoke test.

## Adding a model backend

Drop a module under `aive/models/backends/`, subclass `BaseInferenceBackend`,
register it in `aive/models/registry.py`. Document the VRAM floor and the
expected input tensor layout in the module docstring.

## Reporting bugs

Open an issue with: Windows build, GPU + driver, ffmpeg version, the exact
pipeline you ran, and a redacted log from `logs/aive.log`. Timeline files
(`*.aiveproj`) help enormously — attach one if you can share it.

## Community

Be excellent to each other. We're here to make video editing less painful.