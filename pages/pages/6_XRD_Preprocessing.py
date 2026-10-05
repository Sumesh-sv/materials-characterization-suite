import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import savgol_filter
from scipy import sparse
from scipy.sparse.linalg import spsolve


def remove_nan(two_theta, intensity):
    """
    Remove NaN and infinite values.
    """
    mask = np.isfinite(two_theta) & np.isfinite(intensity)

    return two_theta[mask], intensity[mask]


def gaussian_smoothing(intensity, sigma=1):
    """
    Gaussian smoothing.
    """
    return gaussian_filter1d(intensity, sigma=sigma)


def savgol_smoothing(
        intensity,
        window_length=11,
        polyorder=3
):
    """
    Savitzky-Golay smoothing.
    """
    return savgol_filter(
        intensity,
        window_length=window_length,
        polyorder=polyorder
    )


def als_baseline(
        intensity,
        lam=1e5,
        p=0.01,
        niter=10
):
    """
    Asymmetric Least Squares baseline correction.
    """

    L = len(intensity)

    D = sparse.diags(
        [1, -2, 1],
        [0, -1, -2],
        shape=(L, L-2)
    )

    w = np.ones(L)

    for _ in range(niter):

        W = sparse.spdiags(w, 0, L, L)

        Z = W + lam * D.dot(D.transpose())

        baseline = spsolve(Z, w * intensity)

        w = (
            p * (intensity > baseline)
            + (1-p) * (intensity < baseline)
        )

    return baseline


def normalize(intensity):
    """
    Normalize intensity between 0 and 1.
    """

    return (
        intensity - np.min(intensity)
    ) / (
        np.max(intensity) - np.min(intensity)
    )


def preprocess_xrd(
        two_theta,
        intensity,
        smoothing="Gaussian",
        sigma=1,
        baseline=True,
        normalize_data=True
):
    """
    Complete preprocessing pipeline.
    """

    two_theta, intensity = remove_nan(
        two_theta,
        intensity
    )

    if baseline:

        base = als_baseline(
            intensity
        )

    else:

        base = np.zeros_like(intensity)

    corrected = intensity - base

    if smoothing == "Gaussian":

        smooth = gaussian_smoothing(
            corrected,
            sigma=sigma
        )

    else:

        smooth = savgol_smoothing(
            corrected
        )

    if normalize_data:

        smooth = normalize(
            smooth
        )

    return {

        "two_theta": two_theta,

        "raw": intensity,

        "baseline": base,

        "corrected": corrected,

        "smoothed": smooth

    }
