"""
Supplier routes for Flask API.

Provides endpoints for Supplier domain:
- GET /api/supplier - Get all supplier documents
- GET /api/supplier/<id> - Get a specific supplier document by ID
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.supplier_service import SupplierService

import logging
logger = logging.getLogger(__name__)


def create_supplier_routes():
    """
    Create a Flask Blueprint exposing supplier endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with supplier routes
    """
    supplier_routes = Blueprint('supplier_routes', __name__)
    
    @supplier_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_suppliers():
        """
        GET /api/supplier - Retrieve infinite scroll batch of sorted, filtered supplier documents.
        
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
        result = SupplierService.get_suppliers(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_suppliers Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @supplier_routes.route('/<supplier_id>', methods=['GET'])
    @handle_route_exceptions
    def get_supplier(supplier_id):
        """
        GET /api/supplier/<id> - Retrieve a specific supplier document by ID.
        
        Args:
            supplier_id: The supplier ID to retrieve
            
        Returns:
            JSON response with the supplier document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        supplier = SupplierService.get_supplier(supplier_id, token, breadcrumb)
        logger.info(f"get_supplier Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(supplier), 200
    
    logger.info("Supplier Flask Routes Registered")
    return supplier_routes