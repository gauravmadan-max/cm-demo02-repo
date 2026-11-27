# cm-demo02-repo (OpsPortal API)

Simple Python/Flask internal operations web service for CI/CD security demo workflows.

## Project Structure

- `app/main.py` — Flask HTTP application and API routes
- `app/auth.py` — SQLite user authentication and directory lookup
- `app/files.py` — Operational report download helper
- `app/diagnostics.py` — Host resolution diagnostics helper
- `app/templates_view.py` — Dynamic HTML greeting banner renderer
- `app/profiles.py` — YAML workspace profile importer
- `data/reports/q1_summary.txt` — Sample quarterly status report
- `tests/test_app.py` — Functional test suite (`pytest`)

## Local Setup & Tests

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

Run the server locally:

```bash
python -m app.main
```
