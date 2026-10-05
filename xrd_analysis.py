import numpy as np
from xrd_peak_analysis import detect_peaks

# Cu Kα wavelength (nm)
LAMBDA = 0.15406
def calculate_d_spacing(two_theta, wavelength=LAMBDA):

    theta = np.radians(two_theta / 2)

    d = wavelength / (2 * np.sin(theta))

    return d
def calculate_Lc(
        two_theta,
        fwhm,
        wavelength=LAMBDA,
        K=0.9
):
    """
    Calculate crystallite stacking height (Lc)
    using the Scherrer equation.

    Parameters
    ----------
    two_theta : float
        Peak position (degrees).

    fwhm : float
        FWHM of the peak (degrees).

    wavelength : float
        X-ray wavelength (nm).

    K : float
        Shape factor.

    Returns
    -------
    float
        Lc in nm.
    """

    theta = np.radians(two_theta / 2)

    beta = np.radians(fwhm)

    if beta == 0:
        return np.nan

    Lc = (K * wavelength) / (beta * np.cos(theta))

    return Lc
def calculate_number_of_layers(
        Lc,
        d002
):
    """
    Calculate the number of stacked graphene layers.

    Parameters
    ----------
    Lc : float
        Crystallite stacking height (nm).

    d002 : float
        Interlayer spacing (nm).

    Returns
    -------
    float
        Number of graphene layers.
    """

    if d002 == 0:
        return np.nan

    return (Lc / d002) + 1
def calculate_packing_density(d002):
    """
    Calculate layer packing density.

    Parameters
    ----------
    d002 : float
        Interlayer spacing (nm).

    Returns
    -------
    float
        Layer packing density (g/cm³).
    """

    if d002 == 0:
        return np.nan

    return 0.762 / d002
def calculate_graphitization(d002):
    """
    Calculate the degree of graphitization.

    Parameters
    ----------
    d002 : float
        Interlayer spacing (nm).

    Returns
    -------
    float
        Degree of graphitization (%).
    """

    numerator = 0.3440 - d002
    denominator = 0.3440 - 0.3354

    Y = numerator / denominator

    return Y * 100
def analyze_graphitic_xrd(
        two_theta,
        intensity,
        height=0.05,
        prominence=0.02
):
    """
    Analyze XRD pattern of graphitic materials.

    Parameters
    ----------
    two_theta : numpy.ndarray
        2θ values.

    intensity : numpy.ndarray
        XRD intensity.

    Returns
    -------
    dict
        Complete XRD analysis results.
    """

    peaks = detect_peaks(
        two_theta,
        intensity,
        height=height,
        prominence=prominence
    )

    result = {}

    # -----------------------------
    # Identify graphitic peaks
    # -----------------------------

    peak_002 = None
    peak_100 = None
    peak_004 = None

    for peak in peaks:

        pos = peak["position"]

        if 24 <= pos <= 28:
            peak_002 = peak

        elif 41 <= pos <= 45:
            peak_100 = peak

        elif 53 <= pos <= 56:
            peak_004 = peak

    result["002"] = peak_002
    result["100"] = peak_100
    result["004"] = peak_004

    # -----------------------------
    # Calculate structural parameters
    # -----------------------------

    if peak_002 is not None:

        d002 = calculate_d_spacing(
            peak_002["position"]
        )

        Lc = calculate_Lc(
            peak_002["position"],
            peak_002["FWHM"]
        )

        layers = calculate_number_of_layers(
            Lc,
            d002
        )

        density = calculate_packing_density(
            d002
        )

        graphitization = calculate_graphitization(
            d002
        )

        result["d002"] = d002
        result["Lc"] = Lc
        result["Layers"] = layers
        result["Density"] = density
        result["Graphitization"] = graphitization

    else:

        result["d002"] = np.nan
        result["Lc"] = np.nan
        result["Layers"] = np.nan
        result["Density"] = np.nan
        result["Graphitization"] = np.nan

    return result