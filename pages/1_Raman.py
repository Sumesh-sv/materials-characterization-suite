import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from analysis import analyze_spectrum
from preprocessing import preprocess
from interpretation import interpret_raman
from utils.pdf_report import create_pdf

st.title("🔬 Raman Spectrum Analyzer")
st.subheader("Sample Information")

col1, col2 = st.columns(2)
with col1:

    sample_name = st.text_input(
        "Sample Name"
    )

    material = st.text_input(
        "Material"
    )

    operator = st.text_input(
        "Operator"
    )
with col2:

    laser = st.selectbox(
        "Laser Wavelength",
        [325, 488, 514, 532, 633, 785]
    )

    acquisition_date = st.date_input(
        "Date"
    )

    comments = st.text_area(
        "Comments"
    )
st.sidebar.header("Processing")

sigma = st.sidebar.slider(
    "Gaussian Smoothing",
    0.0,
    5.0,
    1.0,
    0.1
)


peak_height = st.sidebar.number_input(
    "Minimum Peak Height",
    value=100
)

show_baseline = st.sidebar.checkbox(
    "Show Baseline",
    True
)

show_corrected = st.sidebar.checkbox(
    "Show Corrected Spectrum",
    True
)

uploaded = st.file_uploader(
    "Upload Raman Spectrum",
    type=["txt","csv"]
)

if uploaded is not None:

    data = pd.read_csv(
        uploaded,
        delim_whitespace=True,
        header=None
    )

    shift = data.iloc[:,0].values
    intensity = data.iloc[:,1].values
    # ==============================
    # Preprocess Spectrum
    # ==============================

    processed = preprocess(
        shift,
        intensity
    )

    result = analyze_spectrum(
        processed["shift"],
        processed["smoothed"],
        peak_height=peak_height
    )
    result["Baseline"] = processed["baseline"]

    result["Corrected"] = processed["corrected"]

    result["Smoothed"] = processed["smoothed"]

    fig = go.Figure()

    # Raw Spectrum
    fig.add_trace(
        go.Scatter(
            x=shift,
            y=intensity,
            name="Raw Spectrum",
            line=dict(color="red")
        )
    )

    # Baseline
    if show_baseline:
        fig.add_trace(
            go.Scatter(
                x=shift,
                y=result["Baseline"],
                name="Baseline",
                line=dict(color="orange", dash="dash")
            )
        )

    # Corrected Spectrum
    if show_corrected:

        fig.add_trace(
            go.Scatter(
                x=shift,
                y=result["Corrected"],
                name="Corrected Spectrum",
                line=dict(color="green")
            )
        )

        # Define colors FIRST
        colors = {
            "D": "red",
            "G": "green",
            "2D": "blue"
        }

        # Plot Lorentzian Fits
        for key in ["D", "G", "2D"]:

            peak = result[key]

            if peak["found"] and "x_fit" in peak:
                fig.add_trace(
                    go.Scatter(
                        x=peak["x_fit"],
                        y=peak["y_fit"],
                        mode="lines",
                        name=f"{key} Lorentzian Fit",
                        line=dict(
                            width=3,
                            dash="dot"
                        )
                    )
                )

        # Plot Peak Markers
        for key in ["D", "G", "2D"]:

            peak = result[key]

            if peak["found"]:
                fig.add_trace(
                    go.Scatter(
                        x=[peak["position"]],
                        y=[peak["height"]],
                        mode="markers+text",
                        text=[key],
                        textposition="top center",
                        marker=dict(
                            size=12,
                            color=colors[key]
                        ),
                        showlegend=False
                    )
                )


    st.plotly_chart(
        fig,
        use_container_width=True
    )
    plot_filename = "raman_plot.png"

    fig.write_image(
        plot_filename,
        width=1200,
        height=700,
        scale=2
    )

    st.subheader("Peak Information")

    rows = []

    for key in ["D","G","2D"]:

        peak = result[key]

        if peak["found"]:

            rows.append({

                "Peak": key,

                "Position (cm⁻¹)": round(
                    peak["position"],
                    2
                ),

                "Height": round(
                    peak["height"],
                    2
                ),

                "FWHM (cm⁻¹)": round(
                    peak["FWHM"],
                    2
                ),

                "Area": round(
                    peak["area"],
                    2
                ),

                "R²": round(
                    peak["R2"],
                    4
                ),

                "Status": "✓"

            })
        else:

            rows.append({

                "Peak": key,

                "Position (cm⁻¹)": "-",

                "Height": "-",

                "FWHM (cm⁻¹)": "-",

                "Area": "-",

                "R²": "-",

                "Status": "Missing"

            })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True
    )

    st.subheader("📊 Calculated Parameters")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "ID/IG",
            f"{result['IDIG']:.3f}"
            if result["IDIG"] == result["IDIG"]
            else "N/A"
        )

        st.metric(
            "Lsp² (nm)",
            f"{result['Lsp2']:.2f}"
            if result["Lsp2"] == result["Lsp2"]
            else "N/A"
        )

        st.metric(
            "Defect Density",
            f"{result['DefectDensity']:.2e}"
            if result["DefectDensity"] == result["DefectDensity"]
            else "N/A"
        )

    with col2:

        st.metric(
            "I₂D/IG",
            f"{result['I2DIG']:.3f}"
            if result["I2DIG"] == result["I2DIG"]
            else "N/A"
        )

        st.metric(
            "LD (nm)",
            f"{result['LD']:.2f}"
            if result["LD"] == result["LD"]
            else "N/A"
        )

    interpretation = interpret_raman(result)

    for line in interpretation:
        st.write(line)

    st.subheader("Quality Check")

    if not result["D"]["found"]:
        st.error("❌ D peak missing")
    else:
        st.success("✅ D peak detected")

    if not result["G"]["found"]:
        st.error("❌ G peak missing")
    else:
        st.success("✅ G peak detected")

    if not result["2D"]["found"]:
        st.warning("⚠ 2D peak missing")
    else:
        st.success("✅ 2D peak detected")

    csv = pd.DataFrame(rows).to_csv(index=False)

    st.download_button(
        "📥 Download Results",
        csv,
        file_name="RamanResults.csv",
        mime="text/csv"
    )

    st.subheader("📄 PDF Report")

    if st.button("Generate PDF Report"):
        sample_info = {
            "sample_name": sample_name,
            "material": material,
            "operator": operator,
            "comments": comments
        }

        filename = "Raman_Report.pdf"

        create_pdf(
            filename,
            sample_info,
            "Raman Spectroscopy",
            result,
            interpretation,
            figure_path=plot_filename
        )

        with open(filename, "rb") as pdf_file:
            st.download_button(
                label="⬇ Download PDF",
                data=pdf_file,
                file_name=filename,
                mime="application/pdf"
            )
