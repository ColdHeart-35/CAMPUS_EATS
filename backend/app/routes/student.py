# backend/app/routes/student.py
"""Student API endpoints.
- GET /student/menu : list food items with categories
- GET /student/menu/{item_id} : get details of a food item
- POST /student/cart/add : add item to cart (simple in‑memory for demo)
- POST /student/cart/remove : remove item from cart
- POST /student/order : place an order
- GET /student/orders : get order history
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict

from ..dependencies import require_role
from ..services import food, order

router = APIRouter()

# In‑memory cart per user (for demonstration only)
_user_carts: Dict[int, List[Dict[str, int]]] = {}

@router.get("/menu", response_model=List[Dict])
async def get_menu(user: dict = Depends(require_role("student"))):
    return await food.get_all_items()

@router.get("/menu/{item_id}", response_model=Dict)
async def get_item(item_id: int, user: dict = Depends(require_role("student"))):
    item = await food.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/cart/add")
async def add_to_cart(item_id: int, quantity: int = 1, user: dict = Depends(require_role("student"))):
    uid = int(user["sub"])
    cart = _user_carts.setdefault(uid, [])
    # Simple upsert logic
    for entry in cart:
        if entry["item_id"] == item_id:
            entry["quantity"] += quantity
            break
    else:
        cart.append({"item_id": item_id, "quantity": quantity})
    return {"msg": "Added to cart", "cart": cart}

@router.post("/cart/remove")
async def remove_from_cart(item_id: int, user: dict = Depends(require_role("student"))):
    uid = int(user["sub"])
    cart = _user_carts.get(uid, [])
    _user_carts[uid] = [e for e in cart if e["item_id"] != item_id]
    return {"msg": "Removed from cart", "cart": _user_carts[uid]}

@router.post("/order")
async def place_order(payment_method: str, user: dict = Depends(require_role("student"))):
    uid = int(user["sub"])
    cart = _user_carts.get(uid)
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
    order_id = await order.create_order(user_id=uid, cart_items=cart, payment_method=payment_method)
    # clear cart after successful order
    _user_carts[uid] = []
    return {"msg": "Order placed", "order_id": order_id}

@router.get("/orders")
async def order_history(user: dict = Depends(require_role("student"))):
    uid = int(user["sub"])
    return await order.get_orders_by_user(uid)
