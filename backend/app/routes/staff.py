# backend/app/routes/staff.py
"""Staff API endpoints.
- GET /staff/orders : view incoming orders
- POST /staff/orders/{order_id}/status : update order status (accept/reject, etc.)
- POST /staff/food : add new food item
- PUT /staff/food/{item_id} : update food item
- DELETE /staff/food/{item_id} : delete food item
- GET /staff/inventory : view ingredient stock
- POST /staff/inventory/update : adjust stock quantity
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any

from ..dependencies import require_role
from ..services import order, food, inventory

router = APIRouter()

@router.get("/orders", response_model=List[Dict])
async def get_incoming_orders(user: dict = Depends(require_role("staff"))):
    return await order.get_all_pending()

@router.post("/orders/{order_id}/status")
async def update_order_status(order_id: int, new_status: str, user: dict = Depends(require_role("staff"))):
    if new_status not in ["pending", "accepted", "preparing", "ready", "completed", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    await order.set_order_status(order_id, new_status)
    return {"msg": "Status updated"}

@router.post("/food")
async def add_food(item: Dict[str, Any], user: dict = Depends(require_role("staff"))):
    await food.create_food(item)
    return {"msg": "Food item added"}

@router.put("/food/{item_id}")
async def update_food(item_id: int, updates: Dict[str, Any], user: dict = Depends(require_role("staff"))):
    await food.update_food(item_id, updates)
    return {"msg": "Food item updated"}

@router.delete("/food/{item_id}")
async def delete_food(item_id: int, user: dict = Depends(require_role("staff"))):
    await food.delete_food(item_id)
    return {"msg": "Food item deleted"}

@router.get("/inventory", response_model=List[Dict])
async def view_inventory(user: dict = Depends(require_role("staff"))):
    return await inventory.get_all_ingredients()

@router.post("/inventory/update")
async def update_inventory(ingredient_id: int, delta: int, user: dict = Depends(require_role("staff"))):
    await inventory.adjust_stock(ingredient_id, delta)
    return {"msg": "Inventory updated"}
