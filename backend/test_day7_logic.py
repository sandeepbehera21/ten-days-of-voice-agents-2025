import unittest
import os
import json
from src.grocery_tools import GroceryCart, OrderManager, ORDERS_PATH

class TestGroceryAgent(unittest.TestCase):
    def setUp(self):
        # Clear orders file for testing
        if os.path.exists(ORDERS_PATH):
            os.remove(ORDERS_PATH)
        self.cart = GroceryCart()
        self.order_manager = OrderManager()

    def test_add_item(self):
        res = self.cart.add_item("Organic Bananas", 2)
        self.assertIn("Added 2 Organic Bananas", res)
        self.assertEqual(self.cart.items["prod_001"]["quantity"], 2)

    def test_add_invalid_item(self):
        res = self.cart.add_item("Unicorn Meat")
        self.assertIn("couldn't find", res)

    def test_cart_total(self):
        self.cart.add_item("Organic Bananas", 1) # 0.69
        self.cart.add_item("Whole Milk", 1)      # 3.99
        self.assertAlmostEqual(self.cart.get_total(), 4.68)

    def test_place_order(self):
        self.cart.add_item("Organic Bananas", 1)
        res = self.order_manager.place_order(self.cart)
        self.assertIn("Order placed successfully", res)
        
        # Verify file
        with open(ORDERS_PATH, "r") as f:
            orders = json.load(f)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]["status"], "received")
        self.assertEqual(orders[0]["items"][0]["name"], "Organic Bananas")

    def test_track_order(self):
        self.cart.add_item("Organic Bananas", 1)
        self.order_manager.place_order(self.cart)
        
        status = self.order_manager.get_order_status()
        self.assertIn("received", status)

if __name__ == "__main__":
    unittest.main()
