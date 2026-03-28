import sqlite3
from typing import Optional

DB_PATH = "backend/properties.db"
shortlist = []

def get_connection():
    return sqlite3.connect(DB_PATH)

def row_to_dict(row):
    return {
        "id": row[0],
        "external_id": row[1],
        "title": row[2],
        "price": row[3],
        "area": row[4],
        "beds": row[5],
        "baths": row[6],
        "type": row[7],
        "commute": row[8],
        "size": row[9],
        "lat": row[10],
        "lng": row[11],
        "url": row[12],
        "source": row[13],
    }

def value_score(item: dict) -> int:
    return round((item["beds"] * 24) + (item["size"] / 70) - (item["price"] / 10000) - (item["commute"] / 3))

def search_properties(
    area: Optional[str] = None,
    max_price: Optional[int] = None,
    min_beds: Optional[int] = None,
    property_type: Optional[str] = None,
    max_commute: Optional[int] = None,
) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM listings WHERE 1=1"
    params = []

    if area and area.lower() != "all":
        query += " AND lower(area) = ?"
        params.append(area.lower())

    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)

    if min_beds is not None:
        query += " AND beds >= ?"
        params.append(min_beds)

    if property_type and property_type.lower() != "all":
        query += " AND lower(type) = ?"
        params.append(property_type.lower())

    if max_commute is not None:
        query += " AND commute <= ?"
        params.append(max_commute)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    results = [row_to_dict(row) for row in rows]
    return sorted(results, key=value_score, reverse=True)

def get_property_details(property_id: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM listings WHERE id = ?", (property_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"error": "Property not found"}

    item = row_to_dict(row)
    item["value_score"] = value_score(item)
    item["price_per_bed"] = round(item["price"] / max(item["beds"], 1))
    item["price_per_sqft"] = round(item["price"] / max(item["size"], 1))
    return item

def compare_properties(property_ids: list[int]) -> list[dict]:
    return [get_property_details(pid) for pid in property_ids]

def save_shortlist(property_id: int) -> dict:
    if property_id not in shortlist:
        shortlist.append(property_id)
    return {"shortlist": shortlist}

def get_shortlist() -> list[dict]:
    return [get_property_details(pid) for pid in shortlist]