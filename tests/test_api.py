import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from prometheus_client import REGISTRY
from sqlalchemy import text
from testcontainers.community.postgres import PostgresContainer

ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def client():
    # The same Postgres image as docker-compose.yml, so tests meet the
    # database the service really runs on, not a look-alike like SQLite.
    with PostgresContainer("postgres:17", driver="psycopg") as postgres:
        url = postgres.get_connection_url()
        # The real migration builds the table: if it is broken, every test fails.
        config = Config(ROOT / "alembic.ini")
        config.set_main_option("script_location", str(ROOT / "migrations"))
        config.set_main_option("sqlalchemy.url", url)
        command.upgrade(config, "head")
        # Imported only now: app.db reads DATABASE_URL at import time.
        os.environ["DATABASE_URL"] = url
        from app.main import app

        # A crash becomes a 500 response, as in production, not a test error.
        yield TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def empty_tasks(client):
    # Each test starts with no tasks, so tests do not depend on each other.
    from app.db import engine

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE tasks RESTART IDENTITY"))


def requests_counted(method, route, status):
    # Read the counter straight from the app's registry, the same numbers
    # /metrics would show Prometheus.
    labels = {"method": method, "route": route, "status": status}
    return REGISTRY.get_sample_value("http_requests_total", labels) or 0


def test_create_then_read_task(client):
    created = client.post("/tasks", json={"title": "buy skis"})
    assert created.status_code == 201
    task_id = created.json()["id"]

    read = client.get(f"/tasks/{task_id}")
    assert read.json() == {"id": task_id, "title": "buy skis", "done": False}


def test_list_shows_only_this_tests_tasks(client):
    client.post("/tasks", json={"title": "first"})
    client.post("/tasks", json={"title": "second"})

    titles = [task["title"] for task in client.get("/tasks").json()]
    assert titles == ["first", "second"]


def test_update_then_delete_task(client):
    task_id = client.post("/tasks", json={"title": "wax board"}).json()["id"]

    updated = client.put(f"/tasks/{task_id}", json={"title": "wax board", "done": True})
    assert updated.json()["done"] is True

    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_health_is_ok_with_real_db(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_is_503_when_db_down(client, monkeypatch):
    # Stopping the shared Postgres would break the other tests, so here
    # only the answer to "is the DB up?" is faked.
    monkeypatch.setattr("app.main.db_is_up", lambda: False)
    response = client.get("/health")
    assert response.status_code == 503


def test_crash_is_counted_as_500(client):
    before = requests_counted("GET", "/chaos/error", "500")
    assert client.get("/chaos/error").status_code == 500
    assert requests_counted("GET", "/chaos/error", "500") == before + 1


def test_routes_are_labelled_by_template(client):
    before = requests_counted("GET", "/tasks/{task_id}", "404")
    client.get("/tasks/42")
    assert requests_counted("GET", "/tasks/{task_id}", "404") == before + 1

    before = requests_counted("GET", "unmatched", "404")
    client.get("/wp-admin.php")
    assert requests_counted("GET", "unmatched", "404") == before + 1
