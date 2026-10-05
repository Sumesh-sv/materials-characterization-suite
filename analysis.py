import numpy as np
from peak_analysis import analyze_peaks

# ============================
# Constants
# ============================

LAM = 532      # nm
E = 2.33       # eV


# ============================
# Main Raman Analysis
# ============================

def analyze_spectrum(
        shift,
        intensity,
        peak_height=100,
        prominence=20
):
    """
    Analyze an already preprocessed Raman spectrum.

    Parameters
    ----------
    shift : numpy.ndarray
        Raman shift.

    intensity : numpy.ndarray
        Preprocessed Raman intensity.

    peak_height : float
        Minimum peak height.

    prominence : float
        Minimum peak prominence.

    Returns
    -------
    dict
        Raman analysis results.
    """

    # -------------------------------------
    # Detect Peaks
    # -------------------------------------

    peaks = analyze_peaks(
        shift,
        intensity,
        peak_height=peak_height,
        prominence=prominence
    )

    D = peaks["D"]
    G = peaks["G"]
    TD = peaks["2D"]

    result = {}

    # -------------------------------------
    # Store Peak Information
    # -------------------------------------

    result["D"] = D
    result["G"] = G
    result["2D"] = TD

    result["D_FWHM"] = D.get("FWHM", np.nan)
    result["G_FWHM"] = G.get("FWHM", np.nan)
    result["2D_FWHM"] = TD.get("FWHM", np.nan)

    # -------------------------------------
    # ID / IG
    # -------------------------------------

    if D["found"] and G["found"]:

        IDIG = D["height"] / G["height"]

        result["IDIG"] = IDIG

        result["Lsp2"] = (560 / (E ** 4)) / IDIG

        LD2 = (2.4e-10) * (LAM ** 4) / IDIG

        result["LD"] = np.sqrt(LD2)

        result["DefectDensity"] = (
            1.8e22 * IDIG
        ) / (LAM ** 4)

    else:

        result["IDIG"] = np.nan
        result["Lsp2"] = np.nan
        result["LD"] = np.nan
        result["DefectDensity"] = np.nan

    # -------------------------------------
    # I2D / IG
    # -------------------------------------

    if TD["found"] and G["found"]:

        result["I2DIG"] = (
            TD["height"] /
            G["height"]
        )

    else:

        result["I2DIG"] = np.nan

    return result