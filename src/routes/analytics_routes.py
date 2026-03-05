"""
Analytics routes for Flask API.

Provides endpoints for Analytics domain:
- POST /api/analytics - Create a new analytics document
- GET /api/analytics - Get all analytics documents (with optional ?name= query parameter)
- GET /api/analytics/<id> - Get a specific analytics document by ID
- PATCH /api/analytics/<id> - Update a analytics document
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.analytics_service import AnalyticsService

import logging
logger = logging.getLogger(__name__)


def create_analytics_routes():
    """
    Create a Flask Blueprint exposing analytics endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with analytics routes
    """
    analytics_routes = Blueprint('analytics_routes', __name__)
    
    @analytics_routes.route('', methods=['POST'])
    @handle_route_exceptions
    def create_analytics():
        """
        POST /api/analytics - Create a new analytics document.
        
        Request body (JSON):
        {
            "name": "value",
            "description": "value",
            "status": "active",
            ...
        }
        
        Returns:
            JSON response with the created analytics document including _id
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        data = request.get_json() or {}
        analytics_id = AnalyticsService.create_analytics(data, token, breadcrumb)
        analytics = AnalyticsService.get_analytics(analytics_id, token, breadcrumb)
        
        logger.info(f"create_analytics Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(analytics), 201
    
    @analytics_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_analyticss():
        """
        GET /api/analytics - Retrieve infinite scroll batch of sorted, filtered analytics documents.
        
        Query Parameters:
            name: Optional name filter
            after_id: Cursor for infinite scroll (ID of last item from previous batch, omit for first request)
            limit: Items per batch (default: 10, max: 100)
            sort_by: Field to sort by (default: 'name')
            order: Sort order 'asc' or 'desc' (default: 'asc')
        
        Returns:
            JSON response with infinite scroll results: {
                'items': [...],
                'limit': int,
                'has_more': bool,
                'next_cursor': str|None
            }
        
        Raises:
            400 Bad Request: If invalid parameters provided
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        # Get query parameters
        name = request.args.get('name')
        after_id = request.args.get('after_id')
        limit = request.args.get('limit', 10, type=int)
        sort_by = request.args.get('sort_by', 'name')
        order = request.args.get('order', 'asc')
        
        # Service layer validates parameters and raises HTTPBadRequest if invalid
        # @handle_route_exceptions decorator will catch and format the exception
        result = AnalyticsService.get_analyticss(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_analyticss Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @analytics_routes.route('/<analytics_id>', methods=['GET'])
    @handle_route_exceptions
    def get_analytics(analytics_id):
        """
        GET /api/analytics/<id> - Retrieve a specific analytics document by ID.
        
        Args:
            analytics_id: The analytics ID to retrieve
            
        Returns:
            JSON response with the analytics document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        analytics = AnalyticsService.get_analytics(analytics_id, token, breadcrumb)
        logger.info(f"get_analytics Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(analytics), 200
    
    @analytics_routes.route('/<analytics_id>', methods=['PATCH'])
    @handle_route_exceptions
    def update_analytics(analytics_id):
        """
        PATCH /api/analytics/<id> - Update a analytics document.
        
        Args:
            analytics_id: The analytics ID to update
            
        Request body (JSON):
        {
            "name": "new_value",
            "description": "new_value",
            "status": "archived",
            ...
        }
        
        Returns:
            JSON response with the updated analytics document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        data = request.get_json() or {}
        analytics = AnalyticsService.update_analytics(analytics_id, data, token, breadcrumb)
        
        logger.info(f"update_analytics Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(analytics), 200
    
    logger.info("Analytics Flask Routes Registered")
    return analytics_routes