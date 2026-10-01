import streamlit as st

st.set_page_config(
    page_title="Materials Characterization Suite",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Materials Characterization Suite")

st.markdown("""
### Advanced Characterization Software for Carbon Materials

This application provides automated analysis of characterization data
for graphitic and carbon-based materials.

---
""")

col1, col2 = st.columns(2)

with col1:

    st.subheader("🔬 Raman Spectroscopy")

    st.write("""
    ✔ Peak Detection

    ✔ Lorentzian Peak Fitting

    ✔ Defect Analysis

    ✔ Automatic Interpretation

    ✔ CSV Export
    
    ✔ PDF report
    """)

with col2:

    st.subheader("📈 X-Ray Diffraction")

    st.write("""
    ✔ Peak Identification

    ✔ d-spacing

    ✔ Crystallite Size (Lc)

    ✔ Graphitization

    ✔ Automatic Interpretation
    
    ✔ CSV Export and PDF report
    """)

st.markdown("---")

st.subheader("🚀 Coming Soon")

st.write("""
- FTIR Analysis

- Thermogravimetric Analysis (TGA)

- Publication Report Generator
""")

st.markdown("---")

st.caption("Materials Characterization Suite | Version 1.0")