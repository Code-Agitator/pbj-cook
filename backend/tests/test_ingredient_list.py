from app.ingredients import aggregate_ingredients
from conftest import create_meal, register_member


def create_dish(client, headers, name, ingredients):
    response = client.post(
        "/api/dishes",
        headers=headers,
        json={
            "name": name,
            "description": "",
            "image_path": None,
            "tags": ["测试"],
            "cuisine_id": None,
            "source_url": "",
            "ingredients": ingredients,
            "steps": [],
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_aggregate_ingredients_sums_compatible_numeric_quantities():
    assert aggregate_ingredients([
        {"name": "鸡蛋", "quantity": "2", "unit": "个"},
        {"name": " 鸡蛋 ", "quantity": "1.5", "unit": "个"},
        {"name": "盐", "quantity": "少许", "unit": ""},
        {"name": "盐", "quantity": "少许", "unit": ""},
        {"name": "鸡蛋", "quantity": "200", "unit": "克"},
    ]) == [
        {"name": "鸡蛋", "unit": "个", "total": 3.5, "fragments": []},
        {"name": "盐", "unit": "", "total": None, "fragments": ["少许"]},
        {"name": "鸡蛋", "unit": "克", "total": 200, "fragments": []},
    ]


def test_ingredient_list_requires_the_assigned_cook(client, family):
    meal_id = create_meal(client, family["admin_headers"])
    _, member_headers = register_member(client)

    assert client.get("/api/meals/missing/ingredient-list", headers=family["admin_headers"]).status_code == 404
    assert client.get(f"/api/meals/{meal_id}/ingredient-list", headers=family["admin_headers"]).status_code == 403
    assert client.post(f"/api/meals/{meal_id}/cook", headers=member_headers).status_code == 200

    response = client.get(f"/api/meals/{meal_id}/ingredient-list", headers=member_headers)
    assert response.status_code == 200
    assert response.json() == {"meal_id": meal_id, "items": []}


def test_ingredient_list_deduplicates_dishes_and_excludes_skipped(client, family):
    admin_headers = family["admin_headers"]
    _, member_headers = register_member(client)
    meal_id = create_meal(client, admin_headers)
    first = create_dish(client, admin_headers, "番茄炒蛋", [
        {"name": "鸡蛋", "quantity": "2", "unit": "个"},
        {"name": "盐", "quantity": "少许", "unit": ""},
    ])
    second = create_dish(client, admin_headers, "鸡汤", [
        {"name": "鸡蛋", "quantity": "1", "unit": "个"},
        {"name": "水", "quantity": "500", "unit": "毫升"},
    ])

    assert client.post(f"/api/meals/{meal_id}/cook", headers=admin_headers).status_code == 200
    assert client.post(f"/api/meals/{meal_id}/orders/{first}", headers=admin_headers).status_code == 200
    assert client.post(f"/api/meals/{meal_id}/orders/{first}", headers=member_headers).status_code == 200
    assert client.post(f"/api/meals/{meal_id}/orders/{second}", headers=member_headers).status_code == 200
    assert client.post(f"/api/meals/{meal_id}/skips/{second}", headers=admin_headers).status_code == 200

    response = client.get(f"/api/meals/{meal_id}/ingredient-list", headers=admin_headers)
    assert response.status_code == 200
    items = {item["name"]: item for item in response.json()["items"]}
    assert items == {
        "鸡蛋": {"name": "鸡蛋", "unit": "个", "total": 2, "fragments": []},
        "盐": {"name": "盐", "unit": "", "total": None, "fragments": ["少许"]},
    }
