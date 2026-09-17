import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import database
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    database_path = tmp_path / "test.db"
    uploads_path = tmp_path / "uploads"
    monkeypatch.setattr(database, "DB_PATH", database_path)
    monkeypatch.setattr(database, "UPLOAD_DIR", uploads_path)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def family(client):
    response = client.post(
        "/api/auth/setup",
        json={"family_name": "测试家庭", "name": "管理员", "pin": "123456"},
    )
    assert response.status_code == 200
    data = response.json()
    return {
        "admin": data["user"],
        "admin_headers": {"Authorization": f"Bearer {data['token']}"},
    }


def register_member(client, name="成员"):
    response = client.post(
        "/api/auth/register",
        json={"name": name, "pin": "654321", "join_code": ""},
    )
    assert response.status_code == 200
    data = response.json()
    return data["user"], {"Authorization": f"Bearer {data['token']}"}


def create_meal(client, headers):
    response = client.post(
        "/api/meals",
        headers=headers,
        json={
            "meal_type": "dinner",
            "date": "2030-09-16",
            "dining_time": "18:30",
            "deadline": "16:30",
            "title": "契约测试",
        },
    )
    assert response.status_code == 200
    return response.json()["id"]
