import json
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


EXPORT_FOLDER = Path("exports")
EXPORT_FOLDER.mkdir(exist_ok=True)


def export_json(statistics, analysis):

    report = {
        "statistics": statistics,
        "analysis": analysis
    }

    output_file = EXPORT_FOLDER / "software_report.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    return output_file

def export_markdown(statistics, analysis):

    output_file = EXPORT_FOLDER / "software_report.md"

    with open(output_file, "w", encoding="utf-8") as file:

        file.write("# Software Diagnostics Report\n\n")

        file.write("## Project Statistics\n\n")

        file.write(f"- Total Files: {statistics['total_files']}\n")
        file.write(f"- Total Folders: {statistics['total_folders']}\n")
        file.write(f"- Python Files: {statistics['python_files']}\n")
        file.write(f"- Total Lines: {statistics['total_lines']}\n")
        file.write(f"- Largest File: {statistics['largest_file']}\n")
        file.write(f"- Smallest File: {statistics['smallest_file']}\n\n")

        file.write("## Health Score\n\n")

        for key, value in analysis["health"].items():

            file.write(f"- {key.title()}: {value}\n")

        file.write("\n## Suggestions\n\n")

        for suggestion in analysis["suggestions"]:

            file.write(f"- {suggestion}\n")

    return output_file

def export_pdf(statistics, analysis):

    output_file = EXPORT_FOLDER / "software_report.pdf"

    styles = getSampleStyleSheet()

    document = SimpleDocTemplate(str(output_file))

    elements = []

    elements.append(
        Paragraph("<b>Software Diagnostics Report</b>", styles["Title"])
    )

    elements.append(
        Paragraph("<br/><b>Project Statistics</b>", styles["Heading2"])
    )

    elements.append(
        Paragraph(f"Total Files : {statistics['total_files']}", styles["BodyText"])
    )

    elements.append(
        Paragraph(f"Python Files : {statistics['python_files']}", styles["BodyText"])
    )

    elements.append(
        Paragraph(f"Total Lines : {statistics['total_lines']}", styles["BodyText"])
    )

    elements.append(
        Paragraph("<br/><b>Health Score</b>", styles["Heading2"])
    )

    for key, value in analysis["health"].items():

        elements.append(
            Paragraph(f"{key.title()} : {value}", styles["BodyText"])
        )

    elements.append(
        Paragraph("<br/><b>Suggestions</b>", styles["Heading2"])
    )

    for suggestion in analysis["suggestions"]:

        elements.append(
            Paragraph("• " + suggestion, styles["BodyText"])
        )

    document.build(elements)

    return output_file