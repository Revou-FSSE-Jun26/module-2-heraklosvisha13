# locustfile.py (Letakkan di root proyek, sejajar dengan run.py)
import os
from locust import HttpUser, task, between
from dotenv import load_dotenv

# Load .env so LOAD_TEST_USERNAME / LOAD_TEST_PASSWORD are available.
load_dotenv()


class RevoShopUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        # Login sebagai user dari seed
        username = os.getenv('LOAD_TEST_USERNAME')
        password = os.getenv('LOAD_TEST_PASSWORD')

        with self.client.post(
            "/auth/login",
            json={"username": username, "password": password},
            catch_response=True,
        ) as res:
            if res.status_code == 200:
                # res.json() is a method call in Locust/requests, not an attribute.
                token = res.json().get("data", {}).get("token")
                self.headers = {"Authorization": f"Bearer {token}"}
                res.success()
            else:
                self.headers = {}
                res.failure(
                    f"Login failed ({res.status_code}): {res.text}"
                )

    @task
    def sequential_user_journey(self):
        # Product to exercise. Must be a product that HAS stock, otherwise the
        # order endpoint correctly returns 404 "Insufficient stock".
        # (product_id 1 was out of stock, which caused every POST /orders to fail.)
        product_id = 1

        # 1. GET all products
        self.client.get("/products")

        # 2. GET single product by ID
        self.client.get(f"/products/{product_id}")

        # 3. POST a new order (butuh login)
        if self.headers:
            res = self.client.post("/orders",
                json={"items": [{"product_id": product_id, "quantity": 1}]},
                headers=self.headers
            )
            # 4. GET the created order
            if res.status_code == 201:
                order_id = res.json().get("data", {}).get("order_id")
                self.client.get(f"/orders/{order_id}", headers=self.headers)