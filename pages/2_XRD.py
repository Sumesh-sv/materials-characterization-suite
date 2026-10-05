import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from io import BytesIO
import tempfile
import os

from xrd_preprocessing import preprocess_xrd
from xrd_analysis import analyze_graphitic_xrd
from xrd_interpretation import interpret_xrd
from pdf_report import create_pdf


# =========================================================
# PAGE CONFIGURATION
# =========================================================

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


# =========================================================
# SAMPLE INFORMATION
# =========================================================

st.subheader("Sample Information")

col1, col2 = st.columns(2)

with col1:
    sample_name = st.text_input(
        "Sample Name",
        placeholder="e.g. GNP-BJ"
    )

    material = st.text_input(
        "Material",
        placeholder="e.g. Graphene Nanoplatelets"
    )

with col2:
    operator = st.text_input(
        "Operator",
        placeholder="Enter operator name"
    )

    comments = st.text_area(
        "Comments",
        placeholder="Enter additional information about the sample."
    )


# =========================================================
# FILE UPLOAD
# =========================================================

st.subheader("XRD Data")

uploaded_file = st.file_uploader(
    "Upload XRD data file",
    type=["csv", "txt", "dat", "xy"]
)


if uploaded_file is not None:

    st.success(
        f"File uploaded: {uploaded_file.name}"
    )

    # =====================================================
    # READ DATA
    # =====================================================

    try:

        data = pd.read_csv(
            uploaded_file,
            sep=r"\s+",
            comment="#",
            header=None
        )

        data = data.dropna(
            axis=1,
            how="all"
        )

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

        # Remove invalid values
        valid = (
            np.isfinite(two_theta)
            & np.isfinite(intensity)
        )

        two_theta = two_theta[valid]
        intensity = intensity[valid]

        if len(two_theta) < 10:

            st.error(
                "Not enough valid XRD data points were found."
            )

            st.stop()

        st.success(
            f"Loaded {len(two_theta)} XRD data points."
        )

    except Exception as e:

        st.error(
            f"Could not read the XRD file: {e}"
        )

        st.stop()


    # =====================================================
    # RAW XRD PATTERN
    # =====================================================

    st.subheader("Raw XRD Pattern")

    raw_plot_df = pd.DataFrame(
        {
            "Intensity": intensity
        },
        index=two_theta
    )

    st.line_chart(
        raw_plot_df
    )


    # =====================================================
    # SIDEBAR - PREPROCESSING
    # =====================================================

    st.sidebar.header("Preprocessing")

    smoothing = st.sidebar.selectbox(
        "Smoothing method",
        [
            "Gaussian",
            "Savitzky-Golay"
        ]
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


    # =====================================================
    # SIDEBAR - PEAK DETECTION
    # =====================================================

    st.sidebar.header("Peak Detection")

    peak_height = st.sidebar.slider(
        "Peak height",
        min_value=0.0,
        max_value=1.0,
        value=0.05,
        step=0.01
    )

    peak_prominence = st.sidebar.slider(
        "Peak prominence",
        min_value=0.0,
        max_value=1.0,
        value=0.02,
        step=0.01
    )


    # =====================================================
    # ANALYZE BUTTON
    # =====================================================

    if st.button(
        "🔬 Analyze XRD",
        type="primary"
    ):

        with st.spinner(
            "Processing XRD pattern..."
        ):

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
                # XRD ANALYSIS
                # -----------------------------------------

                result = analyze_graphitic_xrd(
                    processed["two_theta"],
                    processed["smoothed"],
                    height=peak_height,
                    prominence=peak_prominence
                )


                # -----------------------------------------
                # INTERPRETATION
                # -----------------------------------------

                interpretation = interpret_xrd(
                    result
                )


                # -----------------------------------------
                # SAMPLE INFORMATION
                # -----------------------------------------

                sample_info = {
                    "sample_name": sample_name,
                    "material": material,
                    "operator": operator,
                    "comments": comments
                }


                # -----------------------------------------
                # SAVE TO SESSION STATE
                # -----------------------------------------

                st.session_state["xrd_result"] = result

                st.session_state["xrd_processed"] = processed

                st.session_state["xrd_interpretation"] = (
                    interpretation
                )

                st.session_state["xrd_sample_info"] = (
                    sample_info
                )

                st.session_state["xrd_filename"] = (
                    uploaded_file.name
                )

                st.success(
                    "XRD analysis completed successfully."
                )

            except Exception as e:

                st.error(
                    f"Error during XRD analysis: {e}"
                )

                st.exception(e)


    # =====================================================
    # RESULTS
    # =====================================================

    if "xrd_result" in st.session_state:

        result = st.session_state[
            "xrd_result"
        ]

        processed = st.session_state[
            "xrd_processed"
        ]

        interpretation = st.session_state[
            "xrd_interpretation"
        ]

        sample_info = st.session_state[
            "xrd_sample_info"
        ]


        st.divider()


        # =================================================
        # STRUCTURAL PARAMETERS
        # =================================================

        st.subheader(
            "XRD Structural Parameters"
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            d002 = result.get(
                "d002",
                np.nan
            )

            if np.isnan(d002):
                d002_display = "N/A"
            else:
                d002_display = f"{d002:.4f}"

            st.metric(
                "d₀₀₂ (nm)",
                d002_display
            )


        with col2:

            Lc = result.get(
                "Lc",
                np.nan
            )

            if np.isnan(Lc):
                Lc_display = "N/A"
            else:
                Lc_display = f"{Lc:.2f}"

            st.metric(
                "Lc (nm)",
                Lc_display
            )


        with col3:

            layers = result.get(
                "Layers",
                np.nan
            )

            if np.isnan(layers):
                layers_display = "N/A"
            else:
                layers_display = f"{layers:.0f}"

            st.metric(
                "Number of Layers",
                layers_display
            )


        col4, col5 = st.columns(2)


        with col4:

            density = result.get(
                "Density",
                np.nan
            )

            if np.isnan(density):
                density_display = "N/A"
            else:
                density_display = f"{density:.3f}"

            st.metric(
                "Packing Density (g/cm³)",
                density_display
            )


        with col5:

            graphitization = result.get(
                "Graphitization",
                np.nan
            )

            if np.isnan(graphitization):
                graphitization_display = "N/A"
            else:
                graphitization_display = (
                    f"{graphitization:.1f}"
                )

            st.metric(
                "Graphitization (%)",
                graphitization_display
            )


        # =================================================
        # DETECTED PEAKS
        # =================================================

        st.subheader(
            "Detected Graphitic Peaks"
        )

        peak_rows = []


        for peak_name in [
            "002",
            "100",
            "004"
        ]:

            peak = result.get(
                peak_name
            )

            if peak is not None:

                peak_rows.append(
                    {
                        "Peak": peak_name,

                        "2θ (°)": round(
                            peak["position"],
                            3
                        ),

                        "Intensity": round(
                            peak["intensity"],
                            4
                        ),

                        "FWHM (°)": round(
                            peak["FWHM"],
                            4
                        ),

                        "Prominence": round(
                            peak["prominence"],
                            4
                        )
                    }
                )


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
                "No characteristic graphitic peaks "
                "were detected."
            )


        # =================================================
        # AUTOMATIC INTERPRETATION
        # =================================================

        st.subheader(
            "Automatic Interpretation"
        )

        for comment in interpretation:

            st.write(
                comment
            )


        # =================================================
        # PROCESSED XRD PATTERN
        # =================================================

        st.subheader(
            "Processed XRD Pattern"
        )

        plot_df = pd.DataFrame(
            {
                "2θ": processed["two_theta"],

                "Raw": processed["raw"],

                "Baseline": processed["baseline"],

                "Corrected": processed["corrected"],

                "Smoothed": processed["smoothed"]
            }
        )

        st.line_chart(
            plot_df.set_index("2θ")
        )


        # =================================================
        # SAMPLE INFORMATION
        # =================================================

        st.subheader(
            "Sample Information"
        )

        info_display = pd.DataFrame(
            {
                "Parameter": [
                    "Sample Name",
                    "Material",
                    "Operator",
                    "Comments"
                ],

                "Value": [
                    sample_info.get(
                        "sample_name",
                        ""
                    ),

                    sample_info.get(
                        "material",
                        ""
                    ),

                    sample_info.get(
                        "operator",
                        ""
                    ),

                    sample_info.get(
                        "comments",
                        ""
                    )
                ]
            }
        )

        st.dataframe(
            info_display,
            use_container_width=True,
            hide_index=True
        )


        # =================================================
        # DOWNLOAD SECTION
        # =================================================

        st.subheader(
            "Download Results"
        )


        # =================================================
        # EXCEL FILE
        # =================================================

        export_df = pd.DataFrame(
            {
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
        )


        excel_buffer = BytesIO()


        try:

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

                info_display.to_excel(
                    writer,
                    index=False,
                    sheet_name="Sample Information"
                )


            excel_data = (
                excel_buffer.getvalue()
            )


            st.download_button(
                label="📥 Download XRD Results",
                data=excel_data,
                file_name="XRD_Results.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                )
            )


        except Exception as e:

            st.error(
                f"Could not generate Excel file: {e}"
            )


        # =================================================
        # PDF REPORT
        # =================================================

        st.subheader(
            "PDF Report"
        )

        st.write(
            "Generate a complete XRD characterization "
            "report containing sample information, "
            "XRD plot, peak information, calculated "
            "parameters, and interpretation."
        )


        if st.button(
            "📄 Generate XRD PDF Report",
            type="secondary"
        ):

            with st.spinner(
                "Generating PDF report..."
            ):

                figure_path = None
                pdf_path = None

                try:

                    # -------------------------------------
                    # CREATE XRD FIGURE
                    # -------------------------------------

                    fig, ax = plt.subplots(
                        figsize=(10, 5)
                    )


                    ax.plot(
                        processed["two_theta"],
                        processed["raw"],
                        label="Raw",
                        linewidth=1
                    )


                    ax.plot(
                        processed["two_theta"],
                        processed["smoothed"],
                        label="Processed",
                        linewidth=1.2
                    )


                    # -------------------------------------
                    # MARK GRAPHITIC PEAKS
                    # -------------------------------------

                    for peak_name in [
                        "002",
                        "100",
                        "004"
                    ]:

                        peak = result.get(
                            peak_name
                        )

                        if peak is not None:

                            peak_position = (
                                peak["position"]
                            )

                            ax.axvline(
                                peak_position,
                                linestyle="--",
                                linewidth=0.8
                            )

                            ax.text(
                                peak_position,
                                peak["intensity"],
                                peak_name,
                                rotation=90,
                                verticalalignment="bottom"
                            )


                    ax.set_xlabel(
                        "2θ (°)"
                    )

                    ax.set_ylabel(
                        "Intensity"
                    )

                    ax.set_title(
                        "XRD Pattern"
                    )

                    ax.legend()

                    ax.grid(
                        alpha=0.25
                    )

                    fig.tight_layout()


                    # -------------------------------------
                    # TEMPORARY IMAGE
                    # -------------------------------------

                    with tempfile.NamedTemporaryFile(
                        suffix=".png",
                        delete=False
                    ) as temp_image:

                        figure_path = (
                            temp_image.name
                        )


                    fig.savefig(
                        figure_path,
                        dpi=200,
                        bbox_inches="tight"
                    )

                    plt.close(fig)


                    # -------------------------------------
                    # TEMPORARY PDF
                    # -------------------------------------

                    with tempfile.NamedTemporaryFile(
                        suffix=".pdf",
                        delete=False
                    ) as temp_pdf:

                        pdf_path = (
                            temp_pdf.name
                        )


                    # -------------------------------------
                    # CREATE PDF
                    # -------------------------------------

                    create_pdf(
                        filename=pdf_path,
                        sample_info=sample_info,
                        analysis_type="XRD",
                        result=result,
                        interpretation=interpretation,
                        figure_path=figure_path
                    )


                    # -------------------------------------
                    # READ PDF
                    # -------------------------------------

                    with open(
                        pdf_path,
                        "rb"
                    ) as pdf_file:

                        pdf_data = (
                            pdf_file.read()
                        )


                    # -------------------------------------
                    # SUCCESS
                    # -------------------------------------

                    st.success(
                        "PDF report generated successfully."
                    )


                    # -------------------------------------
                    # DOWNLOAD PDF
                    # -------------------------------------

                    safe_sample_name = (
                        sample_info.get(
                            "sample_name",
                            ""
                        ).strip()
                    )


                    if not safe_sample_name:

                        safe_sample_name = "XRD"


                    pdf_filename = (
                        f"{safe_sample_name}_XRD_Report.pdf"
                    )


                    st.download_button(
                        label="📥 Download XRD PDF Report",
                        data=pdf_data,
                        file_name=pdf_filename,
                        mime="application/pdf"
                    )


                except Exception as e:

                    st.error(
                        f"Could not generate PDF report: {e}"
                    )

                    st.exception(e)


                finally:

                    # -------------------------------------
                    # CLEAN TEMPORARY FILES
                    # -------------------------------------

                    if figure_path is not None:

                        try:
                            if os.path.exists(
                                figure_path
                            ):
                                os.remove(
                                    figure_path
                                )
                        except Exception:
                            pass


                    if pdf_path is not None:

                        try:
                            if os.path.exists(
                                pdf_path
                            ):
                                os.remove(
                                    pdf_path
                                )
                        except Exception:
                            pass
