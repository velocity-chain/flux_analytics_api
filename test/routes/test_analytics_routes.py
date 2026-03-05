"""
Unit tests for Analytics routes.

These tests validate the Flask route layer for the Analytics domain, using the
generated blueprint factory and mocking out the underlying service and
token/breadcrumb helpers from api_utils.
"""
import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.analytics_routes import create_analytics_routes


class TestAnalyticsRoutes(unittest.TestCase):
    """Test cases for Analytics routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_analytics_routes(),
            url_prefix="/api/analytics",
        )
        self.client = self.app.test_client()

        self.mock_token = {"user_id": "test_user", "roles": ["admin"]}
        self.mock_breadcrumb = {"at_time": "sometime", "correlation_id": "correlation_ID"}

    @patch("src.routes.analytics_routes.create_flask_token")
    @patch("src.routes.analytics_routes.create_flask_breadcrumb")
    @patch("src.routes.analytics_routes.AnalyticsService.create_analytics")
    @patch("src.routes.analytics_routes.AnalyticsService.get_analytics")
    def test_create_analytics_success(
        self,
        mock_get_analytics,
        mock_create_analytics,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test POST /api/analytics for successful creation."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_create_analytics.return_value = "123"
        mock_get_analytics.return_value = {
            "_id": "123",
            "name": "test-analytics",
            "status": "active",
        }

        response = self.client.post(
            "/api/analytics",
            json={"name": "test-analytics", "status": "active"},
        )

        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_create_analytics.assert_called_once()
        mock_get_analytics.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.analytics_routes.create_flask_token")
    @patch("src.routes.analytics_routes.create_flask_breadcrumb")
    @patch("src.routes.analytics_routes.AnalyticsService.get_analyticss")
    def test_get_analyticss_no_filter(
        self,
        mock_get_analyticss,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/analytics without name filter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_analyticss.return_value = {
            "items": [
                {"_id": "123", "name": "analytics1"},
                {"_id": "456", "name": "analytics2"},
            ],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/analytics")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 2)
        mock_get_analyticss.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name=None,
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.analytics_routes.create_flask_token")
    @patch("src.routes.analytics_routes.create_flask_breadcrumb")
    @patch("src.routes.analytics_routes.AnalyticsService.get_analyticss")
    def test_get_analyticss_with_name_filter(
        self,
        mock_get_analyticss,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/analytics with name query parameter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_analyticss.return_value = {
            "items": [{"_id": "123", "name": "test-analytics"}],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/analytics?name=test")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 1)
        mock_get_analyticss.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name="test",
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.analytics_routes.create_flask_token")
    @patch("src.routes.analytics_routes.create_flask_breadcrumb")
    @patch("src.routes.analytics_routes.AnalyticsService.get_analytics")
    def test_get_analytics_success(
        self,
        mock_get_analytics,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/analytics/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_analytics.return_value = {
            "_id": "123",
            "name": "analytics1",
        }

        response = self.client.get("/api/analytics/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_get_analytics.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.analytics_routes.create_flask_token")
    @patch("src.routes.analytics_routes.create_flask_breadcrumb")
    @patch("src.routes.analytics_routes.AnalyticsService.get_analytics")
    def test_get_analytics_not_found(
        self,
        mock_get_analytics,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/analytics/<id> when document is not found."""
        from api_utils.flask_utils.exceptions import HTTPNotFound

        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_analytics.side_effect = HTTPNotFound(
            "Analytics 999 not found"
        )

        response = self.client.get("/api/analytics/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Analytics 999 not found")

    @patch("src.routes.analytics_routes.create_flask_token")
    def test_create_analytics_unauthorized(self, mock_create_token):
        """Test POST /api/analytics when token is invalid."""
        from api_utils.flask_utils.exceptions import HTTPUnauthorized

        mock_create_token.side_effect = HTTPUnauthorized("Invalid token")

        response = self.client.post(
            "/api/analytics",
            json={"name": "test"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
