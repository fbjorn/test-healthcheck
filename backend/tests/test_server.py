from datetime import datetime

from webtest import TestApp

from backend.db import ServiceStatus


def test_empty_response(client: TestApp, db):
    resp = client.get("/status")
    assert resp.status_code == 200
    assert resp.json == []


def test_list_statuses(client: TestApp, db, monkeypatch):
    now = datetime(2020, 7, 1, 10, 0, 0)
    ServiceStatus(url="http://google.com", code=200, date=now, elapsed=0.5).save_to_db()
    resp = client.get("/status")
    assert resp.status_code == 200
    assert resp.json == [
        {
            "ok": True,
            "code": 200,
            "elapsed": 0.5,
            "date": "2020-07-01T10:00:00",
            "url": "http://google.com",
        }
    ]
