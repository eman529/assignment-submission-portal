import pytest
import app as portal


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_submissions.db")
    monkeypatch.setattr(portal, "DATABASE", test_db)
    portal.init_db()
    with portal.app.test_client() as test_client:
        yield test_client


def test_complete_valid_submission_is_saved_and_displayed(client):
    response = client.post("/", data={
        "name": "Ali Khan",
        "reg_no": "FA24-001",
        "title": "DevOps Lab",
        "url": "https://example.com/assignment"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Ali Khan" in response.data
    assert b"FA24-001" in response.data
    assert b"DevOps Lab" in response.data
    assert b"https://example.com/assignment" in response.data


def test_missing_registration_number_is_rejected(client):
    response = client.post("/", data={
        "name": "Ali Khan",
        "reg_no": "",
        "title": "DevOps Lab",
        "url": "https://example.com/assignment"
    })
    assert response.status_code == 200
    assert b"All fields are required." in response.data
    with portal.get_db() as db:
        assert db.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0


def test_invalid_submission_url_is_rejected_and_not_saved(client):
    response = client.post("/", data={
        "name": "Ali Khan",
        "reg_no": "FA24-001",
        "title": "DevOps Lab",
        "url": "not-a-valid-url"
    })
    assert response.status_code == 200
    assert b"valid HTTP or HTTPS URL" in response.data
    with portal.get_db() as db:
        assert db.execute("SELECT COUNT(*) FROM submissions").fetchone()[0] == 0
