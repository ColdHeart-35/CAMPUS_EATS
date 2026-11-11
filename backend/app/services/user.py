# backend/app/services/user.py
"""User related database operations.
All functions use asyncpg connection and return dictionaries.
"""

from typing import Optional, Dict, Any, List

SQL_GET_BY_EMAIL = "SELECT id, email, password_hash, full_name, role FROM users WHERE email = $1"
SQL_GET_BY_ID = "SELECT id, email, full_name, role FROM users WHERE id = $1"
SQL_INSERT = """
INSERT INTO users (email, password_hash, full_name, role)
VALUES ($1, $2, $3, $4)
RETURNING id, email, full_name, role;
"""
SQL_COUNT = "SELECT COUNT(*) FROM users;"
SQL_GET_ALL = "SELECT id, email, full_name, role FROM users ORDER BY id;"
SQL_UPDATE_ROLE = "UPDATE users SET role = $2 WHERE id = $1;"

async def get_user_by_email(conn, email: str) -> Optional[Dict[str, Any]]:
    row = await conn.fetchrow(SQL_GET_BY_EMAIL, email)
    if row:
        return {
            "id": row[0],
            "email": row[1],
            "password_hash": row[2],
            "full_name": row[3],
            "role": row[4],
        }
    return None

async def get_user_by_id(conn, user_id: int) -> Optional[Dict[str, Any]]:
    row = await conn.fetchrow(SQL_GET_BY_ID, user_id)
    if row:
        return {"id": row[0], "email": row[1], "full_name": row[2], "role": row[3]}
    return None

async def create_user(conn, *, email: str, hashed_password: str, full_name: Optional[str] = None, role: str = "student") -> Dict[str, Any]:
    row = await conn.fetchrow(SQL_INSERT, email, hashed_password, full_name, role)
    return {"id": row[0], "email": row[1], "full_name": row[2], "role": row[3]}

async def count_users(conn) -> int:
    row = await conn.fetchrow(SQL_COUNT)
    return row[0]

async def get_all_users(conn) -> List[Dict[str, Any]]:
    rows = await conn.fetch(SQL_GET_ALL)
    return [{"id": r[0], "email": r[1], "full_name": r[2], "role": r[3]} for r in rows]

async def update_user_role(conn, user_id: int, new_role: str) -> None:
    await conn.execute(SQL_UPDATE_ROLE, user_id, new_role)
