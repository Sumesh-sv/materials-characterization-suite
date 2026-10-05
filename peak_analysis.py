import numpy as np
from scipy.signal import find_peaks
from peak_fitting import fit_lorentzian

def detect_peak(
        shift,
        intensity,
        region,
        peak_name,
        min_height=100,
        prominence=20
):
    """
    Detect the strongest Raman peak within a specified region.

    Parameters
    ----------
    shift : numpy.ndarray
        Raman shift.

    intensity : numpy.ndarray
        Preprocessed Raman intensity.

    region : tuple
        (start, end) Raman shift region.

    peak_name : str
        Name of the peak (D, G, 2D).

    min_height : float
        Minimum peak height.

    prominence : float
        Minimum peak prominence.

    Returns
    -------
    dict
        Information about the detected peak.
    """

    # Select only the required Raman region
    mask = (shift >= region[0]) & (shift <= region[1])

    x = shift[mask]
    y = intensity[mask]

    # Detect peaks
    peaks, properties = find_peaks(
        y,
        height=min_height,
        prominence=prominence
    )

    # If no peak is found
    if len(peaks) == 0:

        return {

            "name": peak_name,

            "found": False,

            "position": np.nan,

            "height": np.nan,

            "index": None

        }

    # Highest peak in the region
    best = np.argmax(properties["peak_heights"])

    peak_index = peaks[best]

    return {

        "name": peak_name,

        "found": True,

        "position": x[peak_index],

        "height": y[peak_index],

        "index": peak_index

    }

def analyze_peaks(
        shift,
        intensity,
        peak_height=100,
        prominence=20
):
    """
    Detect D, G and 2D peaks and calculate their FWHM.
    """

    peaks = {}

    # ---------------------------
    # D Peak
    # ---------------------------
    peaks["D"] = detect_peak(
        shift,
        intensity,
        region=(1300, 1400),
        peak_name="D",
        min_height=peak_height,
        prominence=prominence
    )

    if peaks["D"]["found"]:

        fit = fit_lorentzian(
            shift,
            intensity,
            peaks["D"]["position"]
        )

        if fit is not None:
            peaks["D"].update(fit)

    # ---------------------------
    # G Peak
    # ---------------------------
    peaks["G"] = detect_peak(
        shift,
        intensity,
        region=(1500, 1650),
        peak_name="G",
        min_height=peak_height,
        prominence=prominence
    )

    if peaks["G"]["found"]:

        fit = fit_lorentzian(
            shift,
            intensity,
            peaks["G"]["position"]
        )

        if fit is not None:
            peaks["G"].update(fit)

    # ---------------------------
    # 2D Peak
    # ---------------------------
    peaks["2D"] = detect_peak(
        shift,
        intensity,
        region=(2600, 2800),
        peak_name="2D",
        min_height=peak_height,
        prominence=prominence
    )

    if peaks["2D"]["found"]:

        fit = fit_lorentzian(
            shift,
            intensity,
            peaks["2D"]["position"]
        )

        if fit is not None:
            peaks["2D"].update(fit)

    return peaks
