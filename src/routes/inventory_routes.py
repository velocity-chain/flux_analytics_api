"""
Inventory routes for Flask API.

Provides endpoints for Inventory domain:
- GET /api/inventory - Get all inventory documents
- GET /api/inventory/<id> - Get a specific inventory document by ID
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.inventory_service import InventoryService

import logging
logger = logging.getLogger(__name__)


def create_inventory_routes():
    """
    Create a Flask Blueprint exposing inventory endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with inventory routes
    """
    inventory_routes = Blueprint('inventory_routes', __name__)
    
    @inventory_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_inventorys():
        """
        GET /api/inventory - Retrieve infinite scroll batch of sorted, filtered inventory documents.
        
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
        result = InventoryService.get_inventorys(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_inventorys Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @inventory_routes.route('/<inventory_id>', methods=['GET'])
    @handle_route_exceptions
    def get_inventory(inventory_id):
        """
        GET /api/inventory/<id> - Retrieve a specific inventory document by ID.
        
        Args:
            inventory_id: The inventory ID to retrieve
            
        Returns:
            JSON response with the inventory document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        inventory = InventoryService.get_inventory(inventory_id, token, breadcrumb)
        logger.info(f"get_inventory Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(inventory), 200
    
    logger.info("Inventory Flask Routes Registered")
    return inventory_routes