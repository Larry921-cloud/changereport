"""Flask web application for the ITIL 4 Change Enablement Report Generator."""

import os
import json
import base64
import tempfile
import uuid
from pathlib import Path
from collections import namedtuple

import pandas as pd
from flask import (
    Flask, render_template, request, send_file,
    flash, redirect, url_for, jsonify,
)

from changereport.parser import load_change_data
from changereport.analysis import compute_all_analysis
from changereport.charts import generate_all_charts
from changereport.report import generate_report
from changereport.jargon import translate_change


# Temp directory for uploads and generated PDFs
TEMP_DIR = os.path.join(tempfile.gettempdir(), "changereport")
os.makedirs(TEMP_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max upload

# Named tuples for template data
ChartInfo = namedtuple("ChartInfo", ["title", "caption"])
ImplRow = namedtuple("ImplRow", ["name", "count", "hours", "categories"])

CHART_META = [
    ("by_category", ChartInfo(
        "Changes by Network Category",
        "Distribution of changes across different network and system categories."
    )),
    ("by_impact", ChartInfo(
        "Impact Distribution",
        "Expected customer impact level for each change."
    )),
    ("timeline", ChartInfo(
        "Change Activity Timeline",
        "Daily change activity showing busy periods."
    )),
]

ALLOWED_EXTENSIONS = {".txt", ".tsv", ".csv", ".xls", ".xlsx"}


def _allowed_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def _df_to_json_records(df):
    """Convert DataFrame to a list of dicts for client-side filtering."""
    records = []
    for _, row in df.iterrows():
        subject = str(row.get("subject", ""))

        start_str = ""
        start_ts = 0
        if pd.notna(row.get("start_datetime")):
            start_str = row["start_datetime"].strftime("%d %b %Y %H:%M")
            start_ts = int(row["start_datetime"].timestamp())

        dur_str = ""
        duration = row.get("duration_hours")
        if pd.notna(duration):
            try:
                dur = float(duration)
                if dur < 1:
                    dur_str = f"{int(dur * 60)} min"
                else:
                    dur_str = f"{dur:.1f} hrs"
            except (ValueError, TypeError):
                pass

        description = translate_change(row)

        records.append({
            "id": str(row.get("id", "")),
            "subject": subject,
            "category": str(row.get("category", "")),
            "type": str(row.get("type_of_change", "")),
            "start_date": start_str,
            "start_ts": start_ts,
            "impact": str(row.get("impact_description", "")),
            "implementer": str(row.get("customer_name", "")),
            "duration": dur_str,
            "description": description,
        })
    return records


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("index"))

    if not _allowed_file(file.filename):
        flash("Unsupported file format. Please upload .txt, .xls, or .xlsx files.", "error")
        return redirect(url_for("index"))

    title = request.form.get("title", "ITIL 4 Change Enablement Report").strip()
    if not title:
        title = "ITIL 4 Change Enablement Report"

    # Save uploaded file
    file_id = str(uuid.uuid4())[:8]
    suffix = Path(file.filename).suffix
    upload_path = os.path.join(TEMP_DIR, f"upload_{file_id}{suffix}")
    file.save(upload_path)

    try:
        # Run the analysis pipeline
        df = load_change_data(upload_path)

        if df.empty:
            flash("The uploaded file contains no data.", "error")
            return redirect(url_for("index"))

        analysis = compute_all_analysis(df)
        chart_buffers = generate_all_charts(df, analysis)

        # Save DataFrame to temp CSV for later filtered PDF export
        data_path = os.path.join(TEMP_DIR, f"data_{file_id}.csv")
        df.to_csv(data_path, index=False)

        # Convert chart buffers to base64 for inline display
        charts_b64 = {}
        for key, buf in chart_buffers.items():
            buf.seek(0)
            charts_b64[key] = base64.b64encode(buf.read()).decode("utf-8")

        # Prepare full change data as JSON for client-side filtering
        changes_json = _df_to_json_records(df)

        # Gather unique filter values
        categories = sorted([c for c in df["category"].unique()
                            if pd.notna(c) and str(c).strip()])
        change_types = sorted([t for t in df["type_of_change"].unique()
                              if pd.notna(t) and str(t).strip()])
        impacts = sorted([i for i in df["impact_description"].unique()
                         if pd.notna(i) and str(i).strip()])

        # Prepare implementer data
        impl_df = analysis["implementer_workload"]
        implementers = []
        if not impl_df.empty:
            for name, row in impl_df.iterrows():
                hours = f"{row['total_hours']:.1f}" if pd.notna(row["total_hours"]) else "N/A"
                implementers.append(ImplRow(
                    name=str(name),
                    count=int(row["change_count"]),
                    hours=hours,
                    categories=str(row["categories"]),
                ))

        return render_template("results.html",
            title=title,
            data_id=file_id,
            total_changes=analysis["total_changes"],
            high_impact_count=len(analysis["high_impact"]),
            category_count=len(analysis["by_category"]),
            implementer_count=len(impl_df),
            by_type=analysis["by_type"].to_dict(),
            date_range=analysis["date_range"],
            charts=charts_b64,
            chart_info=CHART_META,
            changes_json=json.dumps(changes_json),
            filter_categories=categories,
            filter_types=change_types,
            filter_impacts=impacts,
            implementers=implementers,
        )

    except Exception as e:
        flash(f"Error processing file: {str(e)}", "error")
        return redirect(url_for("index"))

    finally:
        # Clean up uploaded file
        try:
            os.unlink(upload_path)
        except OSError:
            pass


@app.route("/export-pdf", methods=["POST"])
def export_pdf():
    """Generate a filtered PDF report on demand."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    data_id = data.get("data_id", "")
    title = data.get("title", "ITIL 4 Change Enablement Report")
    filters = data.get("filters", {})

    # Load saved DataFrame
    data_path = os.path.join(TEMP_DIR, f"data_{data_id}.csv")
    if not os.path.exists(data_path):
        return jsonify({"error": "Data not found. Please re-upload your file."}), 404

    try:
        df = pd.read_csv(data_path)

        # Parse datetime columns back
        for col in ["start_datetime", "end_datetime"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # Apply filters
        if filters.get("categories"):
            df = df[df["category"].isin(filters["categories"])]

        if filters.get("types"):
            df = df[df["type_of_change"].isin(filters["types"])]

        if filters.get("impacts"):
            df = df[df["impact_description"].isin(filters["impacts"])]

        if filters.get("implementer"):
            search = filters["implementer"].lower()
            df = df[df["customer_name"].str.lower().str.contains(search, na=False)]

        if filters.get("date_from"):
            date_from = pd.to_datetime(filters["date_from"])
            df = df[df["start_datetime"] >= date_from]

        if filters.get("date_to"):
            date_to = pd.to_datetime(filters["date_to"]) + pd.Timedelta(days=1)
            df = df[df["start_datetime"] < date_to]

        if df.empty:
            return jsonify({"error": "No changes match the current filters."}), 400

        # Regenerate analysis, charts, and PDF for filtered data
        analysis = compute_all_analysis(df)
        chart_buffers = generate_all_charts(df, analysis)

        pdf_id = str(uuid.uuid4())[:8]
        pdf_filename = f"change_report_{pdf_id}.pdf"
        pdf_path = os.path.join(TEMP_DIR, pdf_filename)
        generate_report(df, pdf_path, chart_buffers, analysis, title=title)

        return jsonify({"filename": pdf_filename})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/<filename>")
def download(filename):
    """Serve a generated PDF file."""
    # Sanitize filename to prevent path traversal
    safe_name = Path(filename).name
    filepath = os.path.join(TEMP_DIR, safe_name)

    if not os.path.exists(filepath):
        flash("Report file not found. Please generate a new report.", "error")
        return redirect(url_for("index"))

    return send_file(
        filepath,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=safe_name,
    )


def run_web(host="127.0.0.1", port=5000, debug=False):
    """Start the Flask web server."""
    import webbrowser
    import threading

    url = f"http://{host}:{port}"
    print(f"\n{'='*50}")
    print(f"  Change Report Generator - Web Interface")
    print(f"  Open your browser to: {url}")
    print(f"{'='*50}\n")

    # Open browser after a short delay
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open(url)

    if not debug:
        threading.Thread(target=open_browser, daemon=True).start()

    app.run(host=host, port=port, debug=debug)
