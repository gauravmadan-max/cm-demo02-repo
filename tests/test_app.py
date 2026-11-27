"""Happy-path functional tests for OpsPortal API."""

import pytest

from app.main import create_app


@pytest.fixture()
def client(tmp_path):
    db_file = str(tmp_path / "test_opsportal.db")
    app = create_app(db_path=db_file)
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_login_success_and_failure(client):
    ok = client.post(
        "/api/login",
        json={"username": "alice", "password": "alice-demo-pass"},
    )
    assert ok.status_code == 200
    data = ok.get_json()["user"]
    assert data["username"] == "alice"
    assert data["role"] == "operator"
    assert data["token"]

    bad = client.post(
        "/api/login",
        json={"username": "alice", "password": "wrong-password"},
    )
    assert bad.status_code == 401


def test_user_lookup(client):
    resp = client.get("/api/users?username=alice")
    assert resp.status_code == 200
    assert resp.get_json()["user"]["email"] == "alice@opsportal.local"

    missing = client.get("/api/users?username=nobody")
    assert missing.status_code == 404


def test_report_download(client):
    resp = client.get("/api/reports/download?name=q1_summary.txt")
    assert resp.status_code == 200
    assert "OpsPortal Quarterly Summary" in resp.get_data(as_text=True)


def test_diagnostics_host_lookup(client):
    resp = client.get("/api/diagnostics/host?host=localhost")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["host"] == "localhost"
    assert "localhost" in payload["result"] or "127.0.0.1" in payload["result"]


def test_diagnostics_host_lookup_invalid_host(client):
    resp = client.get("/api/diagnostics/host?host=localhost;id")
    assert resp.status_code == 400
    assert "invalid host" in resp.get_json()["error"]


def test_greeting_banner(client):
    resp = client.get("/api/greeting?name=Alice")
    assert resp.status_code == 200
    assert "Welcome, Alice!" in resp.get_data(as_text=True)


def test_profile_import(client):
    yaml_body = "theme: dark\nnotifications: true\nregion: us-central1\n"
    resp = client.post("/api/profiles/import", data=yaml_body, content_type="text/yaml")
    assert resp.status_code == 200
    assert resp.get_json() == {
        "profile": {
            "theme": "dark",
            "notifications": True,
            "region": "us-central1",
        }
    }
