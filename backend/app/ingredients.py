from decimal import Decimal, InvalidOperation


def _number(value):
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None


def aggregate_ingredients(rows):
    grouped = {}
    for row in rows:
        name = str(row.get("name", "")).strip()
        unit = str(row.get("unit", "")).strip()
        quantity = str(row.get("quantity", "")).strip()
        if not name:
            continue

        key = (name.casefold(), unit.casefold())
        item = grouped.setdefault(key, {
            "name": name,
            "unit": unit,
            "numbers": [],
            "fragments": [],
        })
        numeric = _number(quantity)
        if numeric is not None:
            item["numbers"].append(numeric)
        elif quantity and quantity not in item["fragments"]:
            item["fragments"].append(quantity)

    result = []
    for item in grouped.values():
        numeric_total = sum(item["numbers"], Decimal(0)) if item["numbers"] else None
        fragments = list(item["fragments"])
        total = numeric_total if numeric_total is not None and not fragments else None
        if numeric_total is not None and fragments:
            numeric_text = format(numeric_total, "f").rstrip("0").rstrip(".")
            if numeric_text and numeric_text not in fragments:
                fragments.append(numeric_text)
        result.append({
            "name": item["name"],
            "unit": item["unit"],
            "total": float(total) if total is not None else None,
            "fragments": fragments,
        })
    return result
