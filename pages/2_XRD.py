import streamlit as st
import numpy as np
import pandas as pd
from io import BytesIO

from xrd_preprocessing import preprocess_xrd
from xrd_analysis import analyze_graphitic_xrd
from xrd_interpretation import interpret_xrd


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="XRD Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 XRD Analysis Suite")
st.write(
    "Upload an XRD data file to preprocess the pattern, "
    "detect graphitic peaks, and calculate structural parameters."
)


# ---------------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload XRD data file",
    type=["csv", "txt", "dat", "xy"]
)


if uploaded_file is not None:

    st.success(f"File uploaded: {uploaded_file.name}")

    # -----------------------------------------------------
    # READ DATA
    # -----------------------------------------------------

    try:

        # Read the file using whitespace separation
        # This replaces the deprecated delim_whitespace=True
        data = pd.read_csv(
            uploaded_file,
            sep=r"\s+",
            comment="#",
            header=None
        )

        # Remove completely empty columns
        data = data.dropna(axis=1, how="all")

        if data.shape[1] < 2:
            st.error(
                "The uploaded file must contain at least "
                "two columns: 2θ and intensity."
            )
            st.stop()

        two_theta = pd.to_numeric(
            data.iloc[:, 0],
            errors="coerce"
        ).to_numpy()

        intensity = pd.to_numeric(
            data.iloc[:, 1],
            errors="coerce"
        ).to_numpy()

        st.success(
            f"Loaded {len(two_theta)} XRD data points."
        )

    except Exception as e:

        st.error(f"Could not read the XRD file: {e}")
        st.stop()


    # -----------------------------------------------------
    # DISPLAY RAW DATA
    # -----------------------------------------------------

    st.subheader("Raw XRD Pattern")

    st.line_chart(
        pd.DataFrame({
            "Intensity": intensity
        }, index=two_theta)
    )


    # -----------------------------------------------------
    # PREPROCESSING SETTINGS
    # -----------------------------------------------------

    st.sidebar.header("Preprocessing")

    smoothing = st.sidebar.selectbox(
        "Smoothing method",
        ["Gaussian", "Savitzky-Golay"]
    )

    sigma = st.sidebar.slider(
        "Gaussian sigma",
        min_value=0.1,
        max_value=10.0,
        value=1.0,
        step=0.1
    )

    baseline = st.sidebar.checkbox(
        "Baseline correction",
        value=True
    )

    normalize_data = st.sidebar.checkbox(
        "Normalize intensity",
        value=True
    )


    # -----------------------------------------------------
    # ANALYZE BUTTON
    # -----------------------------------------------------

    if st.button(
        "🔬 Analyze XRD",
        type="primary"
    ):

        with st.spinner("Processing XRD pattern..."):

            try:

                # -----------------------------------------
                # PREPROCESSING
                # -----------------------------------------

                processed = preprocess_xrd(
                    two_theta,
                    intensity,
                    smoothing=smoothing,
                    sigma=sigma,
                    baseline=baseline,
                    normalize_data=normalize_data
                )


                # -----------------------------------------
                # ANALYSIS
                # -----------------------------------------

                result = analyze_graphitic_xrd(
                    processed["two_theta"],
                    processed["smoothed"]
                )


                # -----------------------------------------
                # INTERPRETATION
                # -----------------------------------------

                interpretation = interpret_xrd(
                    result
                )


                # Save results
                st.session_state["xrd_result"] = result
                st.session_state["xrd_processed"] = processed
                st.session_state["xrd_interpretation"] = interpretation

                st.success(
                    "XRD analysis completed successfully."
                )

            except Exception as e:

                st.error(
                    f"Error during XRD analysis: {e}"
                )
                st.exception(e)


    # -----------------------------------------------------
    # SHOW RESULTS
    # -----------------------------------------------------

    if "xrd_result" in st.session_state:

        result = st.session_state["xrd_result"]

        st.divider()

        st.subheader("XRD Structural Parameters")


        col1, col2, col3 = st.columns(3)

        with col1:

            d002 = result.get("d002", np.nan)

            st.metric(
                "d₀₀₂ (nm)",
                "N/A" if np.isnan(d002)
                else f"{d002:.4f}"
            )


        with col2:

            Lc = result.get("Lc", np.nan)

            st.metric(
                "Lc (nm)",
                "N/A" if np.isnan(Lc)
                else f"{Lc:.2f}"
            )


        with col3:

            layers = result.get("Layers", np.nan)

            st.metric(
                "Number of Layers",
                "N/A" if np.isnan(layers)
                else f"{layers:.0f}"
            )


        col4, col5 = st.columns(2)

        with col4:

            density = result.get(
                "Density",
                np.nan
            )

            st.metric(
                "Packing Density (g/cm³)",
                "N/A" if np.isnan(density)
                else f"{density:.3f}"
            )


        with col5:

            graphitization = result.get(
                "Graphitization",
                np.nan
            )

            st.metric(
                "Graphitization (%)",
                "N/A" if np.isnan(graphitization)
                else f"{graphitization:.1f}"
            )


        # -------------------------------------------------
        # PEAK INFORMATION
        # -------------------------------------------------

        st.subheader("Detected Graphitic Peaks")

        peak_rows = []

        for peak_name in ["002", "100", "004"]:

            peak = result.get(peak_name)

            if peak is not None:

                peak_rows.append({
                    "Peak": peak_name,
                    "2θ (°)": round(
                        peak["position"], 3
                    ),
                    "Intensity": round(
                        peak["intensity"], 4
                    ),
                    "FWHM (°)": round(
                        peak["FWHM"], 4
                    ),
                    "Prominence": round(
                        peak["prominence"], 4
                    )
                })

        if peak_rows:

            peak_df = pd.DataFrame(
                peak_rows
            )

            st.dataframe(
                peak_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.warning(
                "No characteristic graphitic peaks were detected."
            )


        # -------------------------------------------------
        # INTERPRETATION
        # -------------------------------------------------

        st.subheader("Automatic Interpretation")

        for comment in st.session_state[
            "xrd_interpretation"
        ]:

            st.write(comment)


        # -------------------------------------------------
        # PROCESSED XRD PLOT
        # -------------------------------------------------

        st.subheader("Processed XRD Pattern")

        processed = st.session_state[
            "xrd_processed"
        ]

        plot_df = pd.DataFrame({
            "2θ": processed["two_theta"],
            "Raw": processed["raw"],
            "Baseline": processed["baseline"],
            "Corrected": processed["corrected"],
            "Smoothed": processed["smoothed"]
        })

        st.line_chart(
            plot_df.set_index("2θ")
        )


        # -------------------------------------------------
        # EXCEL DOWNLOAD
        # -------------------------------------------------

        export_data = {
            "Parameter": [
                "d002 (nm)",
                "Lc (nm)",
                "Number of Layers",
                "Packing Density (g/cm³)",
                "Graphitization (%)"
            ],

            "Value": [
                result.get("d002"),
                result.get("Lc"),
                result.get("Layers"),
                result.get("Density"),
                result.get("Graphitization")
            ]
        }

        export_df = pd.DataFrame(
            export_data
        )

        excel_buffer = BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl"
        ) as writer:

            export_df.to_excel(
                writer,
                index=False,
                sheet_name="XRD Results"
            )

            if peak_rows:

                peak_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Detected Peaks"
                )


        st.download_button(
            "📥 Download XRD Results",
            data=excel_buffer.getvalue(),
            file_name="XRD_Results.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )
