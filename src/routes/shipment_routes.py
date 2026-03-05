"""
Shipment routes for Flask API.

Provides endpoints for Shipment domain:
- GET /api/shipment - Get all shipment documents
- GET /api/shipment/<id> - Get a specific shipment document by ID
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.shipment_service import ShipmentService

import logging
logger = logging.getLogger(__name__)


def create_shipment_routes():
    """
    Create a Flask Blueprint exposing shipment endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with shipment routes
    """
    shipment_routes = Blueprint('shipment_routes', __name__)
    
    @shipment_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_shipments():
        """
        GET /api/shipment - Retrieve infinite scroll batch of sorted, filtered shipment documents.
        
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
        result = ShipmentService.get_shipments(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_shipments Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @shipment_routes.route('/<shipment_id>', methods=['GET'])
    @handle_route_exceptions
    def get_shipment(shipment_id):
        """
        GET /api/shipment/<id> - Retrieve a specific shipment document by ID.
        
        Args:
            shipment_id: The shipment ID to retrieve
            
        Returns:
            JSON response with the shipment document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        shipment = ShipmentService.get_shipment(shipment_id, token, breadcrumb)
        logger.info(f"get_shipment Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(shipment), 200
    
    logger.info("Shipment Flask Routes Registered")
    return shipment_routes