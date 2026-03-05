"""
Unit tests for Shipment routes (consume-style, read-only).
"""
import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.shipment_routes import create_shipment_routes


class TestShipmentRoutes(unittest.TestCase):
    """Test cases for Shipment routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_shipment_routes(),
            url_prefix="/api/shipment",
        )
        self.client = self.app.test_client()

        self.mock_token = {"user_id": "test_user", "roles": ["developer"]}
        self.mock_breadcrumb = {"at_time": "sometime", "correlation_id": "correlation_ID"}

    @patch("src.routes.shipment_routes.create_flask_token")
    @patch("src.routes.shipment_routes.create_flask_breadcrumb")
    @patch("src.routes.shipment_routes.ShipmentService.get_shipments")
    def test_get_shipments_success(
        self,
        mock_get_shipments,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/shipment for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_shipments.return_value = {
            "items": [
                {"_id": "123", "name": "shipment1"},
                {"_id": "456", "name": "shipment2"},
            ],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/shipment")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 2)
        mock_get_shipments.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name=None,
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.shipment_routes.create_flask_token")
    @patch("src.routes.shipment_routes.create_flask_breadcrumb")
    @patch("src.routes.shipment_routes.ShipmentService.get_shipments")
    def test_get_shipments_with_name_filter(
        self,
        mock_get_shipments,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/shipment with name query parameter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_shipments.return_value = {
            "items": [{"_id": "123", "name": "test-shipment"}],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/shipment?name=test")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 1)
        mock_get_shipments.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name="test",
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.shipment_routes.create_flask_token")
    @patch("src.routes.shipment_routes.create_flask_breadcrumb")
    @patch("src.routes.shipment_routes.ShipmentService.get_shipment")
    def test_get_shipment_success(
        self,
        mock_get_shipment,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/shipment/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_shipment.return_value = {
            "_id": "123",
            "name": "shipment1",
        }

        response = self.client.get("/api/shipment/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_get_shipment.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.shipment_routes.create_flask_token")
    @patch("src.routes.shipment_routes.create_flask_breadcrumb")
    @patch("src.routes.shipment_routes.ShipmentService.get_shipment")
    def test_get_shipment_not_found(
        self,
        mock_get_shipment,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/shipment/<id> when document is not found."""
        from api_utils.flask_utils.exceptions import HTTPNotFound

        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_shipment.side_effect = HTTPNotFound(
            "Shipment 999 not found"
        )

        response = self.client.get("/api/shipment/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Shipment 999 not found")

    @patch("src.routes.shipment_routes.create_flask_token")
    def test_get_shipments_unauthorized(self, mock_create_token):
        """Test GET /api/shipment when token is invalid."""
        from api_utils.flask_utils.exceptions import HTTPUnauthorized

        mock_create_token.side_effect = HTTPUnauthorized("Invalid token")

        response = self.client.get("/api/shipment")

        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
