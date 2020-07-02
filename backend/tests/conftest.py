import contextlib

import pytest
from webtest import TestApp

from backend.db import Base, create_session
from backend.main import app

connection_string = "postgresql://root:root@db/healthcheck_test"
test_pg_session, test_pg_engine = create_session(connection_string)


@pytest.fixture()
def client() -> TestApp:
    return TestApp(app)


@pytest.fixture()
def db(monkeypatch):
    monkeypatch.setattr("backend.db.session", test_pg_session)
    with contextlib.closing(test_pg_engine.connect()) as con:
        trans = con.begin()
        for table in reversed(Base.metadata.sorted_tables):
            con.execute(table.delete())
        trans.commit()
