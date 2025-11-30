import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Annotated

# --- Data Models ---
# Simple TypedDict-like structures for documentation
# Product: { id, name, price, currency, category, color, description }
# Order: { id, items: [{product_id, quantity}], total, currency, created_at }

# --- Catalog ---
PRODUCTS = [
    {
        "id": "mug-001",
        "name": "Classic White Mug",
        "price": 500,
        "currency": "INR",
        "category": "mug",
        "color": "white",
        "description": "A simple, elegant white stoneware mug."
    },
    {
        "id": "mug-002",
        "name": "Matte Black Coffee Mug",
        "price": 650,
        "currency": "INR",
        "category": "mug",
        "color": "black",
        "description": "Sleek matte black finish, perfect for modern desks."
    },
    {
        "id": "hoodie-001",
        "name": "Developer Hoodie",
        "price": 2500,
        "currency": "INR",
        "category": "hoodie",
        "color": "black",
        "description": "Comfortable cotton hoodie with a minimal code logo."
    },
    {
        "id": "hoodie-002",
        "name": "Cozy Grey Hoodie",
        "price": 2200,
        "currency": "INR",
        "category": "hoodie",
        "color": "grey",
        "description": "Soft fleece lining, great for cold coding nights."
    },
    {
        "id": "tshirt-001",
        "name": "Basic Blue Tee",
        "price": 800,
        "currency": "INR",
        "category": "t-shirt",
        "color": "blue",
        "description": "100% cotton t-shirt in navy blue."
    }
]

ORDERS_FILE = "day9_orders.json"

def _load_orders() -> List[Dict]:
    if not os.path.exists(ORDERS_FILE):
        return []
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def _save_order(order: Dict):
    orders = _load_orders()
    orders.append(order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

def list_products(
    category: Annotated[Optional[str], "Filter by category (e.g., 'mug', 'hoodie')"] = None,
    max_price: Annotated[Optional[int], "Filter by maximum price"] = None,
    color: Annotated[Optional[str], "Filter by color"] = None
) -> str:
    """
    Searches the product catalog based on filters. 
    Returns a formatted string list of products found.
    """
    results = []
    for p in PRODUCTS:
        if category and category.lower() not in p["category"].lower():
            continue
        if max_price and p["price"] > max_price:
            continue
        if color and color.lower() not in p["color"].lower():
            continue
        results.append(p)
    
    if not results:
        return "No products found matching those criteria."
    
    # Format for the LLM to read easily
    output = "Here are the products I found:\n"
    for p in results:
        output += f"- {p['name']} (ID: {p['id']}): {p['currency']} {p['price']} - {p['description']}\n"
    return output

def create_order(
    product_id: Annotated[str, "The ID of the product to buy"],
    quantity: Annotated[int, "The number of items to buy"] = 1
) -> str:
    """
    Creates a new order for a specific product.
    """
    # Find product
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return f"Error: Product with ID '{product_id}' not found."

    total_price = product["price"] * quantity
    
    order = {
        "id": str(uuid.uuid4())[:8],
        "items": [
            {
                "product_id": product_id,
                "name": product["name"],
                "quantity": quantity,
                "unit_price": product["price"]
            }
        ],
        "total": total_price,
        "currency": product["currency"],
        "created_at": datetime.now().isoformat()
    }
    
    _save_order(order)
    
    return f"Order created successfully! Order ID: {order['id']}. Total: {order['currency']} {order['total']}."

def get_last_order() -> str:
    """
    Retrieves the details of the most recently placed order.
    """
    orders = _load_orders()
    if not orders:
        return "You haven't placed any orders yet."
    
    last_order = orders[-1]
    items_desc = ", ".join([f"{i['quantity']}x {i['name']}" for i in last_order["items"]])
    return f"Your last order ({last_order['id']}) was for {items_desc}. Total: {last_order['currency']} {last_order['total']}."
