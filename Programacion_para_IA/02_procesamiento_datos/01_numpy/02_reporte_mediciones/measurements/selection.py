"""Select measurement rounds by the temperature in the north room."""

import numpy as np

from measurements.processing import FloatArray, validate_shape


def select_warm_rounds(readings: FloatArray, threshold: float) -> FloatArray:
    """Return independent complete rows whose north temperature meets the threshold."""
    validate_shape(readings)
    if not np.isfinite(readings).all():
        raise ValueError("Selection requires finite readings")
    if not np.isfinite(threshold):
        raise ValueError("Selection requires a finite threshold")
    return readings[readings[:, 0] >= threshold]
