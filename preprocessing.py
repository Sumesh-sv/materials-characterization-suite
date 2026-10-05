import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import savgol_filter
from scipy import sparse
from scipy.sparse.linalg import spsolve

def remove_nan(shift, intensity):
    """
    Remove NaN or infinite values from Raman spectrum.
    """

    mask = np.isfinite(shift) & np.isfinite(intensity)

    return shift[mask], intensity[mask]

def gaussian_smoothing(intensity, sigma=1):
    """
    Smooth Raman spectrum using Gaussian filter.
    """

    return gaussian_filter1d(intensity, sigma=sigma)

def savgol_smoothing(intensity,
                     window_length=11,
                     polyorder=3):
    """
    Savitzky-Golay smoothing.
    """

    return savgol_filter(
        intensity,
        window_length=window_length,
        polyorder=polyorder
    )
def remove_cosmic_spikes(intensity, threshold=5):
    """
    Remove sharp cosmic-ray spikes using a median filter approach.

    Parameters
    ----------
    intensity : numpy.ndarray
        Raman intensity values.

    threshold : float
        Number of standard deviations above which a point
        is considered a spike.

    Returns
    -------
    corrected : numpy.ndarray
        Spectrum with spikes removed.
    """

    corrected = intensity.copy()

    # Skip first and last point
    for i in range(1, len(intensity)-1):

        # Median of neighbouring points
        local_median = np.median(intensity[i-1:i+2])

        # Local standard deviation
        local_std = np.std(intensity[i-1:i+2])

        if local_std == 0:
            continue

        # Spike detection
        if abs(intensity[i] - local_median) > threshold * local_std:

            corrected[i] = local_median

    return corrected

def als_baseline(intensity, lam=1e5, p=0.01, niter=10):
    """
    Asymmetric Least Squares (ALS) baseline correction.

    Parameters
    ----------
    intensity : numpy.ndarray
        Raman intensity values.

    lam : float
        Smoothness parameter.
        Larger values produce a smoother baseline.

    p : float
        Asymmetry parameter.
        Small values prevent the baseline from fitting the peaks.

    niter : int
        Number of iterations.

    Returns
    -------
    baseline : numpy.ndarray
        Estimated baseline.
    """

    L = len(intensity)

    D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L-2))

    w = np.ones(L)

    for _ in range(niter):

        W = sparse.spdiags(w, 0, L, L)

        Z = W + lam * D.dot(D.transpose())

        baseline = spsolve(Z, w * intensity)

        w = p * (intensity > baseline) + (1 - p) * (intensity < baseline)

    return baseline
def preprocess(
        shift,
        intensity,
        remove_spikes=True,
        baseline_method="ALS",
        smoothing_method="Gaussian",
        sigma=1,
        window_length=11,
        polyorder=3,
        lam=1e5,
        p=0.01):

    """
    Complete Raman spectrum preprocessing pipeline.
    """

    # -------------------------------------------------
    # Step 1 : Remove NaN values
    # -------------------------------------------------

    shift, intensity = remove_nan(shift, intensity)

    # -------------------------------------------------
    # Step 2 : Remove Cosmic Spikes
    # -------------------------------------------------

    if remove_spikes:
        intensity = remove_cosmic_spikes(intensity)

    # -------------------------------------------------
    # Step 3 : Baseline Correction
    # -------------------------------------------------

    if baseline_method == "ALS":

        baseline = als_baseline(
            intensity,
            lam=lam,
            p=p
        )

    else:
        baseline = np.zeros_like(intensity)

    corrected = intensity - baseline

    # -------------------------------------------------
    # Step 4 : Smoothing
    # -------------------------------------------------

    if smoothing_method == "Gaussian":

        smoothed = gaussian_smoothing(
            corrected,
            sigma=sigma
        )

    elif smoothing_method == "Savitzky-Golay":

        smoothed = savgol_smoothing(
            corrected,
            window_length=window_length,
            polyorder=polyorder
        )

    else:

        smoothed = corrected

    # -------------------------------------------------
    # Return Everything
    # -------------------------------------------------

    return {

        "shift": shift,

        "raw": intensity,

        "baseline": baseline,

        "corrected": corrected,

        "smoothed": smoothed

    }
