import numpy as np
from scipy.signal import find_peaks, peak_widths


def detect_peaks(
        two_theta,
        intensity,
        height=0.05,
        prominence=0.02
):
    """
    Detect all XRD peaks.
    """

    peaks, properties = find_peaks(
        intensity,
        height=height,
        prominence=prominence
    )

    results = []

    for i, peak in enumerate(peaks):

        widths = peak_widths(
            intensity,
            [peak],
            rel_height=0.5
        )

        dx = np.mean(np.diff(two_theta))

        fwhm = widths[0][0] * dx

        results.append({

            "position": two_theta[peak],

            "intensity": intensity[peak],

            "FWHM": fwhm,

            "prominence": properties["prominences"][i],

            "index": peak

        })

    return results