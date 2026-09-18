import unittest
import json
import os
import sys

# Ensure BACKEND root is in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from main import app
from db.connection import SessionLocal, engine
from db.models import Base, Order, User
from api.auth import generate_user_token, create_user_account


class TestOrderSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = app.test_client()

        # Create or ensure test user exists
        cls.test_email = "order_tester@example.com"
        cls.user = create_user_account(cls.test_email, "securepass123", "Order Tester")
        if not cls.user:
            session = SessionLocal()
            cls.user = session.query(User).filter(User.email == cls.test_email).first()
            session.close()

        cls.token = generate_user_token(str(cls.user.id), cls.user.email)

    def test_01_create_order_success(self):
        payload = {
            "customer_name": "Ravi Kumar",
            "customer_phone": "9876543210",
            "shipping_address": "Main Road, Opp Post Office",
            "city": "Pithapuram",
            "pincode": "533450",
            "payment_method": "Cash on Delivery",
            "delivery_method": "Standard Store Delivery",
            "items": [
                {
                    "id": "prod-moto-1",
                    "name": "Motorola Edge 40 Neo 5G",
                    "price": 22999,
                    "qty": 1,
                    "image": "https://example.com/moto.jpg"
                }
            ],
            "total_amount": 22999
        }

        response = self.client.post(
            "/api/orders",
            data=json.dumps(payload),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("order", data)
        order = data["order"]
        self.assertTrue(order["order_number"].startswith("ARU-"))
        self.assertEqual(order["customer_name"], "Ravi Kumar")
        self.assertEqual(order["customer_phone"], "9876543210")
        self.assertEqual(len(order["items"]), 1)
        self.assertEqual(order["total_amount"], 22999.0)

        # Store order_number for retrieval test
        self.__class__.created_order_number = order["order_number"]

    def test_02_create_order_validation(self):
        # Missing address
        invalid_payload = {
            "customer_name": "Ravi Kumar",
            "customer_phone": "9876543210",
            "items": [{"name": "Sample Phone", "price": 10000, "qty": 1}]
        }
        res = self.client.post(
            "/api/orders",
            data=json.dumps(invalid_payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.get_json()["success"])

        # Empty items
        no_items_payload = {
            "customer_name": "Ravi Kumar",
            "customer_phone": "9876543210",
            "shipping_address": "Near Gandhi Statue, Pithapuram",
            "items": []
        }
        res2 = self.client.post(
            "/api/orders",
            data=json.dumps(no_items_payload),
            content_type="application/json"
        )
        self.assertEqual(res2.status_code, 400)

    def test_03_list_orders_with_token(self):
        res = self.client.get(
            "/api/orders",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["orders"], list)
        self.assertGreaterEqual(len(data["orders"]), 1)

    def test_04_get_order_by_number(self):
        order_num = getattr(self.__class__, "created_order_number", None)
        if not order_num:
            return
        res = self.client.get(f"/api/orders/{order_num}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["order"]["order_number"], order_num)


if __name__ == "__main__":
    unittest.main()
