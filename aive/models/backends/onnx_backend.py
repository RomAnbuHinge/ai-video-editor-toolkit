"""ONNX Runtime backend. CPU EP by default, CUDA/DML EP when configured."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import onnxruntime as ort

from aive.models.registry import register
from aive.utils.logging_setup import get_logger

log = get_logger("aive.models.backends.onnx")


class OnnxBackend:
    name = "onnxruntime"

    def __init__(self, weights: Path, device: str = "cpu") -> None:
        providers = self._providers_for(device)
        self._session = ort.InferenceSession(str(weights), providers=providers)
        self._input_name = self._session.get_inputs()[0].name
        log.info("onnx session loaded: %s (%s)", weights.name, providers[0])

    @staticmethod
    def _providers_for(device: str) -> list[str]:
        if device == "cuda":
            return ["CUDAExecutionProvider", "CPUExecutionProvider"]
        if device == "dml":
            return ["DmlExecutionProvider", "CPUExecutionProvider"]
        return ["CPUExecutionProvider"]

    def warmup(self) -> None:
        shape = self._session.get_inputs()[0].shape
        dummy = np.zeros([d if isinstance(d, int) else 1 for d in shape], dtype=np.float32)
        self._session.run(None, {self._input_name: dummy})
        log.debug("onnx warmup done")

    def infer(self, frame: np.ndarray, scale: int = 2) -> np.ndarray:
        x = frame.astype(np.float32) / 255.0
        x = np.transpose(x, (2, 0, 1))[None, ...]
        y = self._session.run(None, {self._input_name: x})[0]
        y = np.clip(y[0].transpose(1, 2, 0) * 255.0, 0, 255)
        return y.astype(np.uint8)

    def transcribe(self, path: str, *, language: str = "en"):
        raise NotImplementedError("use the ASR backend for transcription")


def make_backend(weights: Path, device: str = "cpu") -> OnnxBackend:
    backend = OnnxBackend(weights, device)
    register("superres", backend)  # type: ignore[arg-type]
    return backend