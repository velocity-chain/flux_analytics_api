"""
Optimization routes for Flask API.

Provides endpoints for Optimization domain:
- GET /api/optimization - Get all optimization documents
- GET /api/optimization/<id> - Get a specific optimization document by ID
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.optimization_service import OptimizationService

import logging
logger = logging.getLogger(__name__)


def create_optimization_routes():
    """
    Create a Flask Blueprint exposing optimization endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with optimization routes
    """
    optimization_routes = Blueprint('optimization_routes', __name__)
    
    @optimization_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_optimizations():
        """
        GET /api/optimization - Retrieve infinite scroll batch of sorted, filtered optimization documents.
        
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
        result = OptimizationService.get_optimizations(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_optimizations Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @optimization_routes.route('/<optimization_id>', methods=['GET'])
    @handle_route_exceptions
    def get_optimization(optimization_id):
        """
        GET /api/optimization/<id> - Retrieve a specific optimization document by ID.
        
        Args:
            optimization_id: The optimization ID to retrieve
            
        Returns:
            JSON response with the optimization document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        optimization = OptimizationService.get_optimization(optimization_id, token, breadcrumb)
        logger.info(f"get_optimization Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(optimization), 200
    
    logger.info("Optimization Flask Routes Registered")
    return optimization_routes