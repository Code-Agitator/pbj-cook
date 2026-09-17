import pytest

from conftest import create_meal, register_member


def schedule_payload():
    return {
        "name": "晚餐规则",
        "meal_type": "dinner",
        "enabled": True,
        "dining_time": "18:30",
        "create_lead_hours": 10,
        "deadline_lead_minutes": 120,
        "weekdays": [1, 2, 3],
    }


def test_missing_dish_mutations_return_404(client, family):
    headers = family["admin_headers"]
    payload = {
        "name": "不存在",
        "description": "",
        "image_path": None,
        "tags": [],
        "cuisine_id": None,
        "source_url": "",
        "ingredients": [],
        "steps": [],
    }
    assert client.put("/api/dishes/missing", headers=headers, json=payload).status_code == 404
    assert client.delete("/api/dishes/missing", headers=headers).status_code == 404


def test_missing_schedule_mutations_return_404(client, family):
    headers = family["admin_headers"]
    assert client.put("/api/admin/schedules/missing", headers=headers, json=schedule_payload()).status_code == 404
    assert client.delete("/api/admin/schedules/missing", headers=headers).status_code == 404


@pytest.mark.parametrize(
    ("starting_status", "target_status", "expected"),
    [
        ("ordering", "cooking", 200),
        ("ordering", "cancelled", 200),
        ("ordering", "done", 409),
        ("cooking", "done", 200),
        ("cooking", "cancelled", 200),
        ("cooking", "ordering", 409),
        ("done", "ordering", 409),
        ("done", "cancelled", 409),
        ("cancelled", "ordering", 409),
        ("cancelled", "cooking", 409),
    ],
)
def test_meal_status_transition_matrix(client, family, starting_status, target_status, expected):
    headers = family["admin_headers"]
    meal_id = create_meal(client, headers)
    if starting_status == "cooking":
        assert client.patch(f"/api/meals/{meal_id}/status", headers=headers, json={"status": "cooking"}).status_code == 200
    elif starting_status == "done":
        assert client.patch(f"/api/meals/{meal_id}/status", headers=headers, json={"status": "cooking"}).status_code == 200
        assert client.patch(f"/api/meals/{meal_id}/status", headers=headers, json={"status": "done"}).status_code == 200
    elif starting_status == "cancelled":
        assert client.patch(f"/api/meals/{meal_id}/status", headers=headers, json={"status": "cancelled"}).status_code == 200

    response = client.patch(
        f"/api/meals/{meal_id}/status",
        headers=headers,
        json={"status": target_status},
    )
    assert response.status_code == expected


@pytest.mark.parametrize("status", ["done", "cancelled"])
def test_cannot_claim_cook_after_meal_is_terminal(client, family, status):
    headers = family["admin_headers"]
    meal_id = create_meal(client, headers)
    if status == "done":
        assert client.patch(f"/api/meals/{meal_id}/status", headers=headers, json={"status": "cooking"}).status_code == 200
    assert client.patch(f"/api/meals/{meal_id}/status", headers=headers, json={"status": status}).status_code == 200
    assert client.post(f"/api/meals/{meal_id}/cook", headers=headers).status_code == 409


def test_unauthorized_member_cannot_change_meal_status(client, family):
    meal_id = create_meal(client, family["admin_headers"])
    _, member_headers = register_member(client)
    response = client.patch(
        f"/api/meals/{meal_id}/status",
        headers=member_headers,
        json={"status": "cooking"},
    )
    assert response.status_code == 403
