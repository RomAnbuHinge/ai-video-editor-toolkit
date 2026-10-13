# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.9.x   | yes       |
| 0.8.x   | security fixes only |
| < 0.8   | no        |

## Reporting a vulnerability

Email `security@ai-video-editor-toolkit.dev` with a description, a repro, and
the affected component. Do not open a public issue for security problems.

We aim to acknowledge within 72 hours and ship a fix or mitigation within 14
days for confirmed issues.

## Threat model

The editor runs untrusted media files and loads third-party model weights.
The relevant attack surfaces are:

- **Media decoders.** A malformed container or codec stream is the most likely
  memory-safety issue. Decoding runs in a sandboxed worker subprocess when
  `config.pipeline.isolate_decoder = true` (default).
- **Model weights.** ONNX and safetensors files are loaded with `weights_only`
  semantics. Pickled `.pt` checkpoints are rejected unless
  `config.models.allow_pickle = true` is explicitly set.
- **Plugin handlers.** Third-party handlers under `aive/handlers/plugins/` run
  in-process. Only install handlers you trust. A subprocess isolation mode is
  planned for 1.0.
- **Project files.** `*.aiveproj` files are JSON; they may reference arbitrary
  filesystem paths. We never execute paths found in a project file.

## Out of scope

- Denial of service from absurdly large media (use sane inputs).
- Issues that require an already-compromised machine.
- Vulnerabilities in ffmpeg itself — report those upstream.