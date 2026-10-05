import streamlit as st
import numpy as np
import pandas as pd
from io import BytesIO

st.title("XRD Crystallite Size Analysis")

K = 0.9
lam = 0.154056  # nm, Cu Kα

st.write("Enter the XRD parameters for your material.")

# Number of materials
n_materials = st.number_input(
    "Number of materials",
    min_value=1,
    max_value=20,
    value=1,
    step=1
)

results = []

for i in range(int(n_materials)):
    st.subheader(f"Material {i + 1}")

    col1, col2, col3 = st.columns(3)

    with col1:
        material = st.text_input(
            "Material name",
            value=f"Material {i + 1}",
            key=f"material_{i}"
        )

    with col2:
        theta_2 = st.number_input(
            "2θ (degrees)",
            min_value=0.01,
            value=26.5,
            step=0.01,
            format="%.4f",
            key=f"theta_{i}"
        )

    with col3:
        dbeta = st.number_input(
            "FWHM β (degrees)",
            min_value=0.0001,
            value=0.25,
            step=0.01,
            format="%.4f",
            key=f"fwhm_{i}"
        )

    # Calculations
    theta = theta_2 / 2
    theta_rad = np.radians(theta)
    beta = np.radians(dbeta)

    d = lam / (2 * np.sin(theta_rad))
    La = (K * lam) / (beta * np.cos(theta_rad))
    layers = La / d

    results.append({
        "Material": material,
        "2θ (°)": theta_2,
        "FWHM β (°)": dbeta,
        "d (nm)": round(d, 4),
        "Crystallite Size (nm)": round(La, 2),
        "Average Layers": round(layers, 1)
    })

# Results
st.divider()
st.subheader("XRD Results")

df = pd.DataFrame(results)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

# Excel download
excel_buffer = BytesIO()

with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    df.to_excel(
        writer,
        index=False,
        sheet_name="XRD Results"
    )

st.download_button(
    label="📥 Download Results as Excel",
    data=excel_buffer.getvalue(),
    file_name="XRD_Results.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
