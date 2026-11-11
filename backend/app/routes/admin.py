# backend/app/routes/admin.py
"""Admin API endpoints.
- GET /admin/dashboard : overview stats (placeholder)
- GET /admin/users : list all users
- POST /admin/users/{target_user_id}/role : change user role
- GET /admin/reports/sales : sales summary
- GET /admin/inventory : view all inventory
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any

from ..dependencies import require_role
from ..services import user as user_service, order, inventory, food

router = APIRouter()

@router.get("/dashboard")
async def dashboard(current_user: dict = Depends(require_role("admin"))):
    total_users = await user_service.count_users()
    total_orders = await order.count_orders()
    low_stock = await inventory.count_low_stock()
    return {"total_users": total_users, "total_orders": total_orders, "low_stock_items": low_stock}

@router.get("/users", response_model=List[Dict])
async def list_users(current_user: dict = Depends(require_role("admin"))):
    return await user_service.get_all_users()

@router.post("/users/{target_user_id}/role")
async def change_user_role(target_user_id: int, new_role: str, current_user: dict = Depends(require_role("admin"))):
    if new_role not in ["student", "staff", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    await user_service.update_user_role(target_user_id, new_role)
    return {"msg": "Role updated"}

@router.get("/reports/sales")
async def sales_report(current_user: dict = Depends(require_role("admin"))):
    return await order.sales_summary()

@router.get("/inventory", response_model=List[Dict])
async def inventory_overview(current_user: dict = Depends(require_role("admin"))):
    return await inventory.get_all_ingredients()
