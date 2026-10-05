import numpy as np

def interpret_xrd(result):
    """
    Generate automatic interpretation for graphitic materials.
    """

    comments = []

    # -----------------------------
    # Peak Detection
    # -----------------------------

    if result["002"] is not None:

        comments.append(
            f"✓ (002) peak detected at {result['002']['position']:.2f}°."
        )

    else:

        comments.append(
            "✗ (002) peak not detected."
        )

    if result["100"] is not None:

        comments.append(
            f"✓ (100) peak detected at {result['100']['position']:.2f}°."
        )

    if result["004"] is not None:

        comments.append(
            f"✓ (004) peak detected at {result['004']['position']:.2f}°."
        )

    # -----------------------------
    # d-spacing
    # -----------------------------

    if not np.isnan(result["d002"]):

        comments.append(
            f"Interlayer spacing (d₀₀₂) = {result['d002']:.4f} nm."
        )

        if result["d002"] < 0.336:

            comments.append(
                "The interlayer spacing is close to well-ordered graphite."
            )

        elif result["d002"] < 0.340:

            comments.append(
                "The interlayer spacing suggests slightly disordered graphitic stacking."
            )

        else:

            comments.append(
                "The increased interlayer spacing suggests turbostratic or poorly ordered carbon."
            )

    # -----------------------------
    # Crystallite Size
    # -----------------------------

    if not np.isnan(result["Lc"]):

        comments.append(
            f"Crystallite stacking height (Lc) = {result['Lc']:.2f} nm."
        )

    # -----------------------------
    # Number of Layers
    # -----------------------------

    if not np.isnan(result["Layers"]):

        comments.append(
            f"Estimated number of stacked graphene layers = {result['Layers']:.0f}."
        )

    # -----------------------------
    # Graphitization
    # -----------------------------

    if not np.isnan(result["Graphitization"]):

        comments.append(
            f"Degree of graphitization = {result['Graphitization']:.1f}%."
        )

    return comments