# backend/app/services/order.py
"""Order related database operations using asyncpg.
All functions operate directly on an asyncpg connection without cursor objects.
"""

from typing import List, Dict, Any

# SQL statements
SQL_INSERT_ORDER = """
INSERT INTO orders (user_id, status, created_at)
VALUES ($1, 'pending', NOW())
RETURNING id;
"""

SQL_INSERT_ORDER_ITEM = """
INSERT INTO order_items (order_id, food_item_id, quantity, unit_price)
VALUES ($1, $2, $3, $4);
"""

SQL_SELECT_ORDERS_BY_USER = """
SELECT o.id, o.status, o.created_at, o.updated_at
FROM orders o
WHERE o.user_id = $1
ORDER BY o.created_at DESC;
"""

SQL_SELECT_ALL_PENDING = """
SELECT o.id, o.user_id, o.status, o.created_at
FROM orders o
WHERE o.status = 'pending'
ORDER BY o.created_at;
"""

SQL_UPDATE_ORDER_STATUS = """
UPDATE orders SET status = $2, updated_at = NOW() WHERE id = $1;
"""

SQL_COUNT_ORDERS = "SELECT COUNT(*) FROM orders;"

SQL_SALES_SUMMARY = """
SELECT DATE_TRUNC('day', created_at) AS day, SUM(total_amount) AS daily_sales
FROM (
    SELECT o.id, SUM(oi.quantity * oi.unit_price) AS total_amount
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    GROUP BY o.id
) sub
GROUP BY day
ORDER BY day DESC;
"""

# Import the stock update statement from inventory service
from .inventory import SQL_UPDATE_STOCK

async def create_order(conn, *, user_id: int, cart_items: List[Dict[str, int]], payment_method: str) -> int:
    """Create an order and its items, adjusting inventory atomically.
    The `payment_method` argument is currently unused (placeholder for future integration).
    """
    async with conn.transaction():
        # Insert the order record and obtain its id
        order_row = await conn.fetchrow(SQL_INSERT_ORDER, user_id)
        order_id = order_row[0]

        # Helper query to fetch recipe for a food item
        SQL_SELECT_RECIPE = """
            SELECT ingredient_id, amount, unit FROM recipes WHERE food_item_id = $1
        """

        # Insert each order item and adjust stock based on its recipe
        for item in cart_items:
            await conn.execute(
                SQL_INSERT_ORDER_ITEM,
                order_id,
                item["item_id"],
                item["quantity"],
                0.0,  # price placeholder – in a real app calculate actual price
            )
            # Retrieve recipe rows for the food item
            recipe_rows = await conn.fetch(SQL_SELECT_RECIPE, item["item_id"])
            for ing_id, amount, _unit in recipe_rows:
                delta = -int(amount * item["quantity"])  # deduct required amount from stock
                await conn.execute(SQL_UPDATE_STOCK, ing_id, delta)
                # Log inventory transaction (simple text note)
                await conn.execute(
                    "INSERT INTO inventory_transactions (ingredient_id, delta, note) VALUES ($1, $2, $3)",
                    ing_id,
                    delta,
                    f"Order {order_id} item {item['item_id']}"
                )
        return order_id

async def get_orders_by_user(conn, user_id: int) -> List[Dict[str, Any]]:
    rows = await conn.fetch(SQL_SELECT_ORDERS_BY_USER, user_id)
    return [
        {
            "id": r[0],
            "status": r[1],
            "created_at": r[2].isoformat(),
            "updated_at": r[3].isoformat() if r[3] else None,
        }
        for r in rows
    ]

async def get_all_pending(conn) -> List[Dict[str, Any]]:
    rows = await conn.fetch(SQL_SELECT_ALL_PENDING)
    return [{"id": r[0], "user_id": r[1], "status": r[2], "created_at": r[3].isoformat()} for r in rows]

async def set_order_status(conn, order_id: int, new_status: str) -> None:
    await conn.execute(SQL_UPDATE_ORDER_STATUS, order_id, new_status)

async def count_orders(conn) -> int:
    row = await conn.fetchrow(SQL_COUNT_ORDERS)
    return row[0]

async def sales_summary(conn) -> List[Dict[str, Any]]:
    rows = await conn.fetch(SQL_SALES_SUMMARY)
    return [{"day": r[0].date().isoformat(), "daily_sales": float(r[1])} for r in rows]
