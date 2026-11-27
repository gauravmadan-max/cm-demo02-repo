"""Report storage and download helpers."""

import os


DEFAULT_REPORTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "reports")
)


def read_report(filename: str, reports_dir: str = DEFAULT_REPORTS_DIR) -> str:
    """Read a report file from the reports directory."""
    target_path = os.path.join(reports_dir, filename)
    with open(target_path, "r", encoding="utf-8") as report_file:
        return report_file.read()
