"""
Category management route definitions.
"""

from flask import jsonify
from .. import activity_bp
from ..Handlers.category_handlers import CategoryHandlers
from ..Handlers.handlers import ActivityHandlers as activity_handlers  # Import the shared instance

# Initialize category handlers with shared activity handlers
category_handlers = CategoryHandlers(activity_handlers())

@activity_bp.route('/categories', methods=['GET'])
def get_all_categories():
    """Get all category information."""
    response_data, status_code = category_handlers.get_all_categories()
    return jsonify(response_data), status_code

@activity_bp.route('/categories/custom', methods=['POST'])
def add_custom_category():
    """Add a new custom category."""
    response_data, status_code = category_handlers.add_custom_category()
    return jsonify(response_data), status_code

@activity_bp.route('/categories/custom/<string:category_name>', methods=['DELETE'])
def delete_custom_category(category_name):
    """Delete a custom category."""
    response_data, status_code = category_handlers.delete_custom_category(category_name)
    return jsonify(response_data), status_code

@activity_bp.route('/categories/map-app', methods=['POST'])
def map_application_to_category():
    """Map an application to a category."""
    response_data, status_code = category_handlers.map_application_to_category()
    return jsonify(response_data), status_code

@activity_bp.route('/categories/unmap-app', methods=['DELETE'])
def unmap_application_from_category():
    """Remove application category mapping."""
    response_data, status_code = category_handlers.unmap_application_from_category()
    return jsonify(response_data), status_code