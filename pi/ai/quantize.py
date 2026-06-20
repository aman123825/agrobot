"""INT8 post-training quantization helper for Coral Edge TPU deployment.

INT8 models run faster and are required for the Edge TPU. This produces an
INT8 .tflite from a SavedModel using a representative dataset; then compile it
for Coral:

    edgetpu_compiler model_int8.tflite

TensorFlow is imported lazily/guarded so this module imports without it.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def export_int8_tflite(saved_model_dir: str, rep_images: list,
                       out_path: str = "models/model_int8.tflite") -> bool:
    """Quantize a SavedModel to full-INT8 TFLite using rep_images (list of HWC
    uint8/float arrays) as the representative dataset. Returns True on success.
    """
    try:
        import numpy as np
        import tensorflow as tf
    except Exception as exc:
        logger.warning("TensorFlow/numpy unavailable (%s)", exc)
        return False

    def representative_dataset():
        for img in rep_images:
            arr = np.asarray(img, dtype=np.float32)
            yield [np.expand_dims(arr, axis=0)]

    converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_dataset
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.uint8
    converter.inference_output_type = tf.uint8
    tflite_model = converter.convert()
    with open(out_path, "wb") as fh:
        fh.write(tflite_model)
    logger.info("wrote INT8 model to %s (now run edgetpu_compiler)", out_path)
    return True
