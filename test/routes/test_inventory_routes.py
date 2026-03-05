"""
Unit tests for Inventory routes (consume-style, read-only).
"""
import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.inventory_routes import create_inventory_routes


class TestInventoryRoutes(unittest.TestCase):
    """Test cases for Inventory routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_inventory_routes(),
            url_prefix="/api/inventory",
        )
        self.client = self.app.test_client()

        self.mock_token = {"user_id": "test_user", "roles": ["developer"]}
        self.mock_breadcrumb = {"at_time": "sometime", "correlation_id": "correlation_ID"}

    @patch("src.routes.inventory_routes.create_flask_token")
    @patch("src.routes.inventory_routes.create_flask_breadcrumb")
    @patch("src.routes.inventory_routes.InventoryService.get_inventorys")
    def test_get_inventorys_success(
        self,
        mock_get_inventorys,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/inventory for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_inventorys.return_value = {
            "items": [
                {"_id": "123", "name": "inventory1"},
                {"_id": "456", "name": "inventory2"},
            ],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/inventory")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 2)
        mock_get_inventorys.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name=None,
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.inventory_routes.create_flask_token")
    @patch("src.routes.inventory_routes.create_flask_breadcrumb")
    @patch("src.routes.inventory_routes.InventoryService.get_inventorys")
    def test_get_inventorys_with_name_filter(
        self,
        mock_get_inventorys,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/inventory with name query parameter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_inventorys.return_value = {
            "items": [{"_id": "123", "name": "test-inventory"}],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/inventory?name=test")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 1)
        mock_get_inventorys.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name="test",
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.inventory_routes.create_flask_token")
    @patch("src.routes.inventory_routes.create_flask_breadcrumb")
    @patch("src.routes.inventory_routes.InventoryService.get_inventory")
    def test_get_inventory_success(
        self,
        mock_get_inventory,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/inventory/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_inventory.return_value = {
            "_id": "123",
            "name": "inventory1",
        }

        response = self.client.get("/api/inventory/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_get_inventory.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.inventory_routes.create_flask_token")
    @patch("src.routes.inventory_routes.create_flask_breadcrumb")
    @patch("src.routes.inventory_routes.InventoryService.get_inventory")
    def test_get_inventory_not_found(
        self,
        mock_get_inventory,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/inventory/<id> when document is not found."""
        from api_utils.flask_utils.exceptions import HTTPNotFound

        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_inventory.side_effect = HTTPNotFound(
            "Inventory 999 not found"
        )

        response = self.client.get("/api/inventory/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Inventory 999 not found")

    @patch("src.routes.inventory_routes.create_flask_token")
    def test_get_inventorys_unauthorized(self, mock_create_token):
        """Test GET /api/inventory when token is invalid."""
        from api_utils.flask_utils.exceptions import HTTPUnauthorized

        mock_create_token.side_effect = HTTPUnauthorized("Invalid token")

        response = self.client.get("/api/inventory")

        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
