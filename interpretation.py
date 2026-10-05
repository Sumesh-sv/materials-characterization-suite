import numpy as np

def interpret_raman(result):
    """
    Generate automatic interpretation for graphitic materials.
    """

    comments = []

    # ======================================================
    # Peak Detection
    # ======================================================

    comments.append("### Peak Detection")

    if result["G"]["found"]:
        comments.append(
            f"✓ G band detected at {result['G']['position']:.2f} cm⁻¹."
        )
    else:
        comments.append("✗ G band not detected.")
    # -----------------------------
    # G Band Position Analysis
    # -----------------------------

    if result["G"]["found"]:

        g_pos = result["G"]["position"]

        if 1578 <= g_pos <= 1585:

            comments.append(
                "The G band position is within the expected range for graphitic carbon."
            )

        elif g_pos < 1578:

            comments.append(
                "The G band is shifted to lower Raman shift, which may indicate tensile strain or other sample-related effects."
            )

        else:

            comments.append(
                "The G band is shifted to higher Raman shift, which may indicate compressive strain, doping, or other sample-related effects."
            )

    if result["D"]["found"]:

        d_pos = result["D"]["position"]

        comments.append(
            f"✓ D band detected at {d_pos:.2f} cm⁻¹."
        )

        if 1340 <= d_pos <= 1365:

            comments.append(
                "The D band position is characteristic of defect-activated graphitic carbon."
            )

        elif d_pos < 1340:

            comments.append(
                "The D band appears at a lower Raman shift than typically observed. This may arise from sample-specific effects or experimental conditions."
            )

        else:

            comments.append(
                "The D band appears at a higher Raman shift than typically observed. This may arise from sample-specific effects or experimental conditions."
            )

    else:

        comments.append(
            "✓ D band not detected."
        )

    if result["2D"]["found"]:

        td_pos = result["2D"]["position"]

        comments.append(
            f"✓ 2D band detected at {td_pos:.2f} cm⁻¹."
        )

        if 2680 <= td_pos <= 2735:

            comments.append(
                "The 2D band position is typical of graphitic materials measured using a 532 nm excitation laser."
            )

        elif td_pos < 2680:

            comments.append(
                "The 2D band appears at a lower Raman shift than typically observed. This may reflect sample-specific effects or experimental conditions."
            )

        else:

            comments.append(
                "The 2D band appears at a higher Raman shift than typically observed. This may reflect sample-specific effects or experimental conditions."
            )

    else:

        comments.append(
            "✗ 2D band not detected."
        )

    # ======================================================
    # Defect Analysis
    # ======================================================

    comments.append("")
    comments.append("### Defect Analysis")

    if not np.isnan(result["IDIG"]):

        comments.append(f"ID/IG = {result['IDIG']:.3f}")

        if result["IDIG"] < 0.2:
            comments.append(
                "Very low defect density."
            )

        elif result["IDIG"] < 0.5:
            comments.append(
                "Low defect density."
            )

        elif result["IDIG"] < 1:
            comments.append(
                "Moderate defect density."
            )

        else:
            comments.append(
                "High defect density."
            )

    # ======================================================
    # Layer Analysis
    # ======================================================

    comments.append("")
    comments.append("### Layer Analysis")
    # -----------------------------
    # 2D Peak FWHM
    # -----------------------------

    if result["2D"]["found"]:

        fwhm = result["2D"]["FWHM"]

        comments.append(
            f"2D FWHM = {fwhm:.2f} cm⁻¹"
        )

        if fwhm < 35:

            comments.append(
                "Very narrow 2D band, characteristic of monolayer graphene."
            )

        elif fwhm < 60:

            comments.append(
                "2D band width is consistent with bilayer or few-layer graphene."
            )

        elif fwhm < 90:

            comments.append(
                "Broad 2D band suggests few-layer graphene."
            )

        else:

            comments.append(
                "Very broad 2D band, typical of multilayer graphene or graphite."
            )

    if not np.isnan(result["I2DIG"]):

        comments.append(
            f"I2D/IG = {result['I2DIG']:.3f}"
        )

        if result["I2DIG"] > 2:

            comments.append(
                "Consistent with monolayer graphene."
            )

        elif result["I2DIG"] > 1:

            comments.append(
                "Consistent with few-layer graphene."
            )

        else:

            comments.append(
                "Consistent with multilayer graphene or graphite."
            )
    # ======================================================
    # Peak Width Analysis
    # ======================================================

    comments.append("")
    comments.append("### Peak Width Analysis")
    if result["G"]["found"]:

        g_fwhm = result["G"]["FWHM"]

        comments.append(
            f"G FWHM = {g_fwhm:.2f} cm⁻¹"
        )

        if g_fwhm < 20:

            comments.append(
                "The G band is very narrow, indicating excellent graphitic crystallinity."
            )

        elif g_fwhm < 35:

            comments.append(
                "The G band width is consistent with good graphitic crystallinity."
            )

        else:

            comments.append(
                "The broadened G band may indicate increased structural disorder or defects."
            )
    if result["D"]["found"]:

        d_fwhm = result["D"]["FWHM"]

        comments.append(
            f"D FWHM = {d_fwhm:.2f} cm⁻¹"
        )

        if d_fwhm < 30:

            comments.append(
                "The D band is relatively narrow, suggesting localized structural defects."
            )

        elif d_fwhm < 60:

            comments.append(
                "The D band width is consistent with moderate structural disorder."
            )

        else:

            comments.append(
                "The broad D band indicates a high degree of structural disorder."
            )
    if result["2D"]["found"]:

        td_fwhm = result["2D"]["FWHM"]

        comments.append(
            f"2D FWHM = {td_fwhm:.2f} cm⁻¹"
        )

        if td_fwhm < 35:

            comments.append(
                "The very narrow 2D band is characteristic of monolayer graphene."
            )

        elif td_fwhm < 60:

            comments.append(
                "The 2D band width is consistent with bilayer or few-layer graphene."
            )

        elif td_fwhm < 90:

            comments.append(
                "The broad 2D band suggests few-layer graphene."
            )

        else:

            comments.append(
                "The very broad 2D band is typical of multilayer graphene or graphite."
            )
    # ======================================================
    # Overall Assessment
    # ======================================================

    comments.append("")
    comments.append("### Overall Assessment")

    if (
        not np.isnan(result["IDIG"]) and
        not np.isnan(result["I2DIG"])
    ):

        if result["IDIG"] < 0.2 and result["I2DIG"] > 1:

            comments.append(
                "The Raman spectrum is consistent with high-quality few-layer graphene with low defect density."
            )

        elif result["IDIG"] < 0.5:

            comments.append(
                "The Raman spectrum indicates graphitic carbon with relatively low structural disorder."
            )

        elif result["IDIG"] < 1:

            comments.append(
                "The Raman spectrum indicates graphitic carbon with a moderate level of defects."
            )

        else:

            comments.append(
                "The Raman spectrum indicates highly defective graphitic carbon."

            )

    return comments