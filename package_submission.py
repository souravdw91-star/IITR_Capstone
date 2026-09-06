"""
Submission Packaging Script for CloudServe Capstone Project.
Generates PDF formatted deliverables with dynamic DB stats & exact values,
and packages them into a clean submission archive.

Usage:
    python package_submission.py --name "Sourav_Nayak"
"""
import os
import re
import shutil
import zipfile
import argparse

from pdf_generator import fetch_live_db_and_metrics_data, create_pdf_from_markdown


def clean_name_formats(raw_name: str):
    """
    Parses input name (e.g. 'Sourav_Nayak' or 'Sourav Nayak') into:
    - display_name: 'Sourav Nayak'
    - file_prefix:  'SouravNayak'
    """
    clean_parts = [p for p in re.split(r'[\s_]+', raw_name.strip()) if p]
    display_name = " ".join(clean_parts)
    file_prefix = "".join(clean_parts)
    return display_name, file_prefix


def package_submission(raw_author_name: str):
    display_name, file_prefix = clean_name_formats(raw_author_name)

    archive_name = f"{file_prefix}_Capstone_Submission.zip"
    build_dir = f"temp_submission_build"

    print(f"=== Packaging Capstone Submission for '{display_name}' ===")

    # 1. Fetch Dynamic Database & Evaluation Data
    live_data = fetch_live_db_and_metrics_data()
    print(f"  [LIVE DATA] Database Total Decisions: {live_data['db_total_decisions']}")
    print(f"  [LIVE DATA] Auto-Respond Count:       {live_data['db_auto_respond']}")
    print(f"  [LIVE DATA] Escalation Count:         {live_data['db_escalated']}")
    print(f"  [LIVE DATA] Evaluation FCR:           {live_data['eval_fcr_pct']}%")
    print(f"  [LIVE DATA] Evaluation Escalation:    {live_data['eval_escalation_pct']}%\n")

    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)

    # ---------------------------------------------------------
    # 01_Video Folder
    # ---------------------------------------------------------
    v_dir = os.path.join(build_dir, "01_Video")
    os.makedirs(v_dir, exist_ok=True)
    video_link_file = os.path.join(v_dir, "video_link.txt")
    with open(video_link_file, "w", encoding="utf-8") as f:
        f.write(f"CloudServe Capstone Project Demonstration Video\n")
        f.write(f"Author / Engineer: {display_name}\n")
        f.write(f"Date: {live_data['eval_timestamp']}\n")
        f.write(f"Video URL / File: [Insert MP4 Video Link or Recording Path Here]\n")

    # ---------------------------------------------------------
    # 02_Report Folder (Rendered PDF)
    # ---------------------------------------------------------
    r_dir = os.path.join(build_dir, "02_Report")
    os.makedirs(r_dir, exist_ok=True)

    report_md_path = "docs/Project_Report.md"
    if os.path.exists(report_md_path):
        with open(report_md_path, "r", encoding="utf-8") as f:
            report_content = f.read()

        # Inject dynamic author name & live data into report
        report_content = report_content.replace("Forward Deployed AI Engineer", display_name)
        report_content = report_content.replace("Author:** Forward Deployed AI Engineer", f"Author:** {display_name}")

        report_pdf_path = os.path.join(r_dir, f"{file_prefix}_Capstone_Report.pdf")
        create_pdf_from_markdown(
            md_content=report_content,
            output_pdf_path=report_pdf_path,
            title="CloudServe Support System — Project Report",
            author_name=display_name
        )

    # ---------------------------------------------------------
    # 03_Workbooks Folder (Rendered PDFs)
    # ---------------------------------------------------------
    w_dir = os.path.join(build_dir, "03_Workbooks")
    os.makedirs(w_dir, exist_ok=True)

    workbooks_to_process = [
        ("docs/workbooks/Stage_1_Discovery_Workbook.md", "Stage_1_Discovery_Workbook.pdf", "Stage 1 — Discovery Workbook"),
        ("docs/workbooks/Stage_2_PRD.md", "Stage_2_PRD.pdf", "Stage 2 — Product Requirements Document (PRD v1)"),
        ("docs/workbooks/Stage_3_Prompt_Library.md", "Stage_3_Prompt_Library.pdf", "Stage 3 — Prompt Library & Specification"),
        ("docs/workbooks/Stage_4_Sprint_Plan.md", "Stage_4_Sprint_Plan.pdf", "Stage 4 — Sprint Plan & Backlog"),
        ("docs/workbooks/Stage_5_PRD_Revision_Log.md", "Stage_5_PRD_Revision_Log.pdf", "Stage 5 — PRD Revision Log"),
        ("docs/workbooks/Effort_Log.md", f"{file_prefix}_Effort_Log.pdf", "Capstone Project Effort Log")
    ]

    for src_md, pdf_dest_name, doc_title in workbooks_to_process:
        if os.path.exists(src_md):
            with open(src_md, "r", encoding="utf-8") as f:
                wb_content = f.read()

            # Inject author name & dynamic stats into workbook content
            wb_content = wb_content.replace("Forward Deployed AI Engineer", display_name)
            wb_content = wb_content.replace("Author:** Forward Deployed AI Engineer", f"Author:** {display_name}")

            # Append Live Database & Metric Evidence Section to workbooks
            wb_content += f"\n\n---\n## Live Audit & Database Verification Metrics\n"
            wb_content += f"- **Database Decision Records:** {live_data['db_total_decisions']} total decisions logged in `decisions.db`\n"
            wb_content += f"- **Auto-Responses:** {live_data['db_auto_respond']} | **Escalations:** {live_data['db_escalated']} | **Guardrail Blocks:** {live_data['db_blocked']}\n"
            wb_content += f"- **Unattended Evaluation FCR Rate:** {live_data['eval_fcr_pct']}%\n"
            wb_content += f"- **P95 Latency:** {live_data['eval_p95_latency']}s | **Citation Accuracy:** {live_data['eval_citation_accuracy']}%\n"

            dest_pdf_path = os.path.join(w_dir, pdf_dest_name)
            create_pdf_from_markdown(
                md_content=wb_content,
                output_pdf_path=dest_pdf_path,
                title=doc_title,
                author_name=display_name
            )

    # ---------------------------------------------------------
    # 04_Source_Code Folder
    # ---------------------------------------------------------
    src_code_dir = os.path.join(build_dir, "04_Source_Code")
    os.makedirs(src_code_dir, exist_ok=True)

    items_to_copy = [
        "src", "prompts", "tests", "evaluation", "docs", "data",
        "README.md", "requirements.txt", ".env.example", ".gitignore",
        "run_tests.py", "streamlit_app.py", "pdf_generator.py", "package_submission.py", ".github"
    ]

    for item in items_to_copy:
        if os.path.exists(item):
            dest = os.path.join(src_code_dir, item)
            if os.path.isdir(item):
                shutil.copytree(item, dest, ignore=shutil.ignore_patterns("__pycache__", ".venv", "*.pyc", ".pytest_cache"))
            else:
                shutil.copy(item, dest)

    # Compress into single ZIP archive
    with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, build_dir)
                zipf.write(full_path, rel_path)

    try:
        shutil.rmtree(build_dir)
    except Exception:
        pass

    print(f"\n[SUCCESS] Submission ZIP created successfully: {archive_name}\n")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Package Capstone Submission with PDF Deliverables")
    parser.add_argument("--name", required=True, help="Your Full Name (e.g. 'Sourav_Nayak')")
    args = parser.parse_args()
    package_submission(args.name)
