import numpy as np
from scipy.optimize import curve_fit

def lorentzian(x, A, x0, gamma, y0):
    """
    Lorentzian function.

    Parameters
    ----------
    A : Peak amplitude
    x0 : Peak center
    gamma : Half-width at half-maximum (HWHM)
    y0 : Offset

    Returns
    -------
    Lorentzian curve
    """

    return y0 + A * (gamma**2) / ((x - x0)**2 + gamma**2)

def fit_lorentzian(
        shift,
        intensity,
        peak_position,
        window=40
):
    """
    Fit a Lorentzian peak around an approximate peak position.

    Parameters
    ----------
    shift : numpy.ndarray
        Raman shift.

    intensity : numpy.ndarray
        Raman intensity.

    peak_position : float
        Approximate peak position.

    window : float
        Half-width of fitting window (cm^-1).

    Returns
    -------
    dict
        Fitted peak parameters.
    """

    # -----------------------------
    # Select fitting region
    # -----------------------------

    mask = (
        (shift >= peak_position - window) &
        (shift <= peak_position + window)
    )

    x = shift[mask]
    y = intensity[mask]

    # Not enough points
    if len(x) < 10:

        return None

    # -----------------------------
    # Initial Guess
    # -----------------------------

    A0 = np.max(y) - np.min(y)

    x0 = peak_position

    gamma0 = 15

    y00 = np.min(y)

    p0 = [A0, x0, gamma0, y00]

    # -----------------------------
    # Fit
    # -----------------------------

    try:

        popt, pcov = curve_fit(
            lorentzian,
            x,
            y,
            p0=p0,
            maxfev=10000
        )

    except Exception as e:

        print("Lorentzian fitting failed:", e)

        return None

    A, x0, gamma, y0 = popt
    peak_height = A + y0

    fitted = lorentzian(
        x,
        *popt
    )

    # -----------------------------
    # Calculate FWHM
    # -----------------------------

    fwhm = 2 * abs(gamma)

    # -----------------------------
    # Peak Area
    # -----------------------------

    area = np.pi * abs(A) * abs(gamma)

    # -----------------------------
    # R²
    # -----------------------------

    residual = y - fitted

    ss_res = np.sum(residual**2)

    ss_tot = np.sum((y - np.mean(y))**2)

    r2 = 1 - (ss_res / ss_tot)

    # -----------------------------
    # Return Results
    # -----------------------------

    return {

        "position": x0,

        "height": peak_height,

        "FWHM": fwhm,

        "area": area,

        "R2": r2,

        "x_fit": x,

        "y_fit": fitted
    }

