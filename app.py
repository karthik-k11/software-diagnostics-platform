from flask import Flask, render_template, request, redirect, flash, send_file
import os
import shutil
import zipfile

from scanner import scan_project
from analyzer import analyze_project
from exporter import export_json, export_markdown, export_pdf
from history_db import initialize_database, save_scan, get_history, delete_scan, clear_history, search_history, history_summary


from datetime import datetime

app = Flask(__name__)
latest_statistics = None
latest_analysis = None
app.secret_key = "software_diagnostics_platform"

UPLOAD_FOLDER = "uploads"
EXTRACT_FOLDER = os.path.join(UPLOAD_FOLDER, "extracted")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACT_FOLDER, exist_ok=True)
initialize_database()


@app.route("/")
def home():
    return render_template(
    "index.html",
    statistics=None,
    analysis=None
)


@app.route("/upload", methods=["POST"])
def upload():

    uploaded_file = request.files.get("project_zip")

    if uploaded_file is None or uploaded_file.filename == "":
        flash("Please choose a ZIP file.")
        return redirect("/")

    if not uploaded_file.filename.lower().endswith(".zip"):
        flash("Only ZIP files are allowed.")
        return redirect("/")

    zip_path = os.path.join(UPLOAD_FOLDER, "project.zip")

    uploaded_file.save(zip_path)

    if os.path.exists(EXTRACT_FOLDER):
        shutil.rmtree(EXTRACT_FOLDER)

    os.makedirs(EXTRACT_FOLDER)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(EXTRACT_FOLDER)

    global latest_statistics
    global latest_analysis

    statistics = scan_project(EXTRACT_FOLDER)

    analysis = analyze_project(
        EXTRACT_FOLDER,
        statistics
    )

    latest_statistics = statistics
    latest_analysis = analysis

    save_scan(

        project_name=uploaded_file.filename,

        scan_date=datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        ),

        overall_score=analysis["health"]["overall"],

        total_files=statistics["total_files"],

        total_lines=statistics["total_lines"],

        warnings=len(analysis["suggestions"])

    )

    return render_template(
        "index.html",
        statistics=statistics,
        analysis=analysis
    )

@app.route("/export/json")
def export_json_report():

    if latest_statistics is None:
        return "No report available."

    file_path = export_json(
        latest_statistics,
        latest_analysis
    )

    return send_file(
        file_path,
        as_attachment=True
    )
@app.route("/export/markdown")
def export_markdown_report():

    if latest_statistics is None:
        return "No report available."

    file_path = export_markdown(
        latest_statistics,
        latest_analysis
    )

    return send_file(
        file_path,
        as_attachment=True
    )

@app.route("/export/pdf")
def export_pdf_report():

    if latest_statistics is None:
        return "No report available."

    file_path = export_pdf(
        latest_statistics,
        latest_analysis
    )

    return send_file(
        file_path,
        as_attachment=True
    )

@app.route("/history")
def history():

    keyword = request.args.get("search", "").strip()

    if keyword:
        history_data = search_history(keyword)
    else:
        history_data = get_history()

    summary = history_summary()

    return render_template(

        "history.html",

        history=history_data,

        summary=summary,

        search=keyword

    )

@app.route("/history/delete/<int:scan_id>")
def delete_history(scan_id):

    delete_scan(scan_id)

    return redirect("/history")

@app.route("/history/clear")
def clear_all_history():

    clear_history()

    return redirect("/history")

if __name__ == "__main__":
    app.run(debug=True)