from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Image

def create_pdf(
        filename,
        sample_info,
        analysis_type,
        result,
        interpretation,
        figure_path=None
):
    """
    Create a simple PDF report.
    """

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    elements = []
    print(elements)

    elements.append(
        Paragraph(
            "<b>Materials Characterization Suite</b>",
            styles["Title"]
        )
    )
    elements.append(
        Paragraph(
            f"<b>{analysis_type} Report</b>",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 12))

    elements.append(
        Spacer(1, 20)
    )

    elements.append(
        Paragraph(
            "<b>Sample Information</b>",
            styles["Heading2"]
        )
    )

    sample_table = [
        ["Sample Name", str(sample_info.get("sample_name", ""))],
        ["Material", str(sample_info.get("material", ""))],
        ["Operator", str(sample_info.get("operator", ""))],
        ["Comments", str(sample_info.get("comments", ""))]
    ]
    table = Table(sample_table, colWidths=[120, 300])

    table.setStyle(

        TableStyle([

            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),

            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),

            ("TOPPADDING", (0, 0), (-1, -1), 8),

            ("FONTNAME", (0, 0), (-1, -1), "Helvetica")

        ])

    )

    elements.append(table)

    elements.append(Spacer(1, 20))
    elements.append(
        Paragraph(
            "<b>Plot</b>",
            styles["Heading2"]
        )
    )

    elements.append(
        Spacer(1, 10)
    )

    if figure_path is not None:
        img = Image(
            figure_path,
            width=450,
            height=260
        )

        elements.append(img)

        elements.append(
            Spacer(1, 20)
        )
        elements.append(
            Paragraph(
                "<b>Peak Information</b>",
                styles["Heading2"]
            )
        )

        if analysis_type == "Raman Spectroscopy":

            peak_table = [
                ["Peak", "Position", "FWHM", "Area"]
            ]

            for peak_name in ["D", "G", "2D"]:

                peak = result[peak_name]

                if peak["found"]:

                    peak_table.append([
                        peak_name,
                        f"{peak['position']:.2f}",
                        f"{peak['FWHM']:.2f}",
                        f"{peak['area']:.2f}"
                    ])

                else:

                    peak_table.append([
                        peak_name,
                        "Missing",
                        "-",
                        "-"
                    ])

        else:

            peak_table = [
                ["Peak", "2θ", "FWHM", "Intensity"]
            ]

            for peak_name in ["002", "100", "004"]:

                peak = result[peak_name]

                if peak is not None:

                    peak_table.append([
                        peak_name,
                        f"{peak['position']:.2f}",
                        f"{peak['FWHM']:.2f}",
                        f"{peak['intensity']:.2f}"
                    ])

                else:

                    peak_table.append([
                        peak_name,
                        "Missing",
                        "-",
                        "-"
                    ])
        peak_tbl = Table(peak_table)

        peak_tbl.setStyle(

            TableStyle([

                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),

                ("ALIGN", (0, 0), (-1, -1), "CENTER"),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 6)

            ])

        )

        elements.append(peak_tbl)

        elements.append(Spacer(1, 20))
        elements.append(
            Paragraph(
                "<b>Calculated Parameters</b>",
                styles["Heading2"]
            )
        )
        if analysis_type == "Raman Spectroscopy":

            parameter_table = [

                ["Parameter", "Value"],

                ["ID/IG", f"{result['IDIG']:.3f}"],

                ["I₂D/IG", f"{result['I2DIG']:.3f}"],

                ["Lsp² (nm)", f"{result['Lsp2']:.2f}"],

                ["LD (nm)", f"{result['LD']:.2f}"],

                ["Defect Density", f"{result['DefectDensity']:.3e}"]

            ]

        else:

            parameter_table = [

                ["Parameter", "Value"],

                ["d002 (nm)", f"{result['d002']:.4f}"],

                ["Lc (nm)", f"{result['Lc']:.2f}"],
                ["Layers", f"{result['Layers']:.1f}"],
                ["Packing Density", f"{result['Density']:.3f}"],
                ["Graphitization (%)", f"{result['Graphitization']:.1f}"]

            ]
        param_tbl = Table(
            parameter_table,
            colWidths=[180, 180]
        )

        param_tbl.setStyle(

            TableStyle([

                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),

                ("ALIGN", (0, 0), (-1, -1), "CENTER"),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 6)

            ])

        )

        elements.append(param_tbl)

        elements.append(
            Spacer(1, 20)
        )
        elements.append(
            Paragraph(
                "<b>Interpretation</b>",
                styles["Heading2"]
            )
        )

        elements.append(
            Spacer(1, 10)
        )
        for line in interpretation:
            elements.append(

                Paragraph(
                    line,
                    styles["BodyText"]
                )

            )
        elements.append(
            Spacer(1, 20)
        )

        elements.append(
            Paragraph(
                "<b>Generated by Materials Characterization Suite</b>",
                styles["Italic"]
            )
        )

    doc.build(elements)
