import json

from bottle import Bottle, response, run  # noqa: F401

from backend.db import ServiceStatus, create_tables
from backend.settings import load_settings_from_env

app = Bottle()


@app.get("/status")
def list_statuses():
    resp = [
        {
            "ok": status.code == 200,
            "code": status.code,
            "elapsed": status.elapsed,
            "date": status.date.isoformat(),
            "url": status.url,
        }
        for status in ServiceStatus.list_all()
    ]
    response.content_type = "application/json"
    return json.dumps(resp, indent=2)


def run_server():
    settings = load_settings_from_env()
    create_tables(settings)
    run(
        host="0.0.0.0",
        port=8080,
        debug=settings.debug,
        reloader=settings.reload,
        app=app,
    )


if __name__ == "__main__":
    run_server()
