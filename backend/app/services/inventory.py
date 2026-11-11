# backend/app/services/inventory.py
"""Inventory related database operations.
Provides functions to list ingredients and adjust stock.
"""

from typing import List, Dict, Any

SQL_GET_ALL = """
SELECT i.id, i.name, i.quantity, i.unit
FROM ingredients i
ORDER BY i.name;
"""

SQL_UPDATE_STOCK = """
UPDATE ingredients SET quantity = quantity + $2 WHERE id = $1 RETURNING quantity;
"""

SQL_COUNT_LOW_STOCK = """
SELECT COUNT(*) FROM ingredients WHERE quantity < 10;
"""

async def get_all_ingredients(conn) -> List[Dict[str, Any]]:
    rows = await conn.fetch(SQL_GET_ALL)
    return [{"id": r[0], "name": r[1], "quantity": r[2], "unit": r[3]} for r in rows]

async def adjust_stock(conn, ingredient_id: int, delta: int) -> int:
    row = await conn.fetchrow(SQL_UPDATE_STOCK, ingredient_id, delta)
    new_qty = row[0]
    if new_qty < 0:
        raise Exception("Inventory cannot be negative")
    return new_qty

async def count_low_stock(conn) -> int:
    row = await conn.fetchrow(SQL_COUNT_LOW_STOCK)
    return row[0]
