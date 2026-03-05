"""
Organization routes for Flask API.

Provides endpoints for Organization domain:
- GET /api/organization - Get all organization documents
- GET /api/organization/<id> - Get a specific organization document by ID
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.organization_service import OrganizationService

import logging
logger = logging.getLogger(__name__)


def create_organization_routes():
    """
    Create a Flask Blueprint exposing organization endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with organization routes
    """
    organization_routes = Blueprint('organization_routes', __name__)
    
    @organization_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_organizations():
        """
        GET /api/organization - Retrieve infinite scroll batch of sorted, filtered organization documents.
        
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
        result = OrganizationService.get_organizations(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_organizations Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @organization_routes.route('/<organization_id>', methods=['GET'])
    @handle_route_exceptions
    def get_organization(organization_id):
        """
        GET /api/organization/<id> - Retrieve a specific organization document by ID.
        
        Args:
            organization_id: The organization ID to retrieve
            
        Returns:
            JSON response with the organization document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        organization = OrganizationService.get_organization(organization_id, token, breadcrumb)
        logger.info(f"get_organization Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(organization), 200
    
    logger.info("Organization Flask Routes Registered")
    return organization_routes