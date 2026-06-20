"""Shared TFLite loading helper with optional Coral Edge TPU delegation.

Tries, in order: tflite_runtime (with libedgetpu delegate when use_coral),
then full TensorFlow's bundled interpreter. Returns None if neither is present
so callers can degrade gracefully instead of crashing on import.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def load_interpreter(model_path: str, use_coral: bool = False):
    """Return an allocated TFLite interpreter, or None if unavailable."""
    Interpreter = None
    load_delegate = None
    try:
        from tflite_runtime.interpreter import Interpreter, load_delegate  # type: ignore
    except Exception:
        try:
            from tensorflow.lite.python.interpreter import Interpreter  # type: ignore

            try:
                from tensorflow.lite.python.interpreter import load_delegate  # type: ignore
            except Exception:
                load_delegate = None
        except Exception as exc:
            logger.warning("TFLite unavailable (%s)", exc)
            return None

    delegates = []
    if use_coral and load_delegate is not None:
        for lib in ("libedgetpu.so.1", "libedgetpu.so.1.0"):
            try:
                delegates = [load_delegate(lib)]
                logger.info("Coral Edge TPU delegate loaded (%s)", lib)
                break
            except Exception:
                delegates = []
        if not delegates:
            logger.info("Coral delegate not found; running TFLite on CPU")

    try:
        interpreter = (
            Interpreter(model_path=model_path, experimental_delegates=delegates)
            if delegates
            else Interpreter(model_path=model_path)
        )
        interpreter.allocate_tensors()
        return interpreter
    except Exception as exc:
        logger.warning("Failed to load model %s (%s)", model_path, exc)
        return None


def read_labels(path: str) -> list[str]:
    """Read a newline-delimited labels file; empty list if missing."""
    try:
        with open(path, encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip()]
    except OSError:
        return []
