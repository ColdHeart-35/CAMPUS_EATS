# backend/app/services/food.py
"""Food service with CRUD operations.
Used by staff routes to manage food items.
"""

from typing import List, Dict, Any, Optional

SQL_GET_ALL = """
SELECT fi.id, fi.name, fi.description, fi.price, c.name AS category
FROM food_items fi
JOIN categories c ON fi.category_id = c.id
ORDER BY fi.name;
"""

SQL_GET_BY_ID = """
SELECT fi.id, fi.name, fi.description, fi.price, c.name AS category
FROM food_items fi
JOIN categories c ON fi.category_id = c.id
WHERE fi.id = $1;
"""

SQL_INSERT = """
INSERT INTO food_items (name, description, price, category_id)
VALUES ($1, $2, $3, $4)
RETURNING id;
"""

SQL_UPDATE = """
UPDATE food_items SET name = $2, description = $3, price = $4, category_id = $5
WHERE id = $1;
"""

SQL_DELETE = "DELETE FROM food_items WHERE id = $1;"

async def get_all_items(conn) -> List[Dict[str, Any]]:
    rows = await conn.fetch(SQL_GET_ALL)
    return [{
        "id": r[0],
        "name": r[1],
        "description": r[2],
        "price": float(r[3]),
        "category": r[4]
    } for r in rows]

async def get_item_by_id(conn, item_id: int) -> Optional[Dict[str, Any]]:
    row = await conn.fetchrow(SQL_GET_BY_ID, item_id)
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": float(row[3]),
            "category": row[4]
        }
    return None

async def create_food(conn, item: Dict[str, Any]) -> int:
    row = await conn.fetchrow(
        SQL_INSERT,
        item["name"],
        item.get("description"),
        item["price"],
        item["category_id"]
    )
    return row[0]

async def update_food(conn, item_id: int, updates: Dict[str, Any]) -> None:
    await conn.execute(
        SQL_UPDATE,
        item_id,
        updates.get("name"),
        updates.get("description"),
        updates.get("price"),
        updates.get("category_id")
    )

async def delete_food(conn, item_id: int) -> None:
    await conn.execute(SQL_DELETE, item_id)
