"""
Category management request handlers.
"""

from flask import jsonify, request
import logging
from typing import Dict, Any

from ..config import *

logger = logging.getLogger(__name__)


class CategoryHandlers:
    """Handles category management operations."""
    
    def __init__(self, activity_handlers):
        self.activity_handlers = activity_handlers
        self.tracker = activity_handlers.tracker
        self.tracker_lock = activity_handlers.tracker_lock
    
    def get_all_categories(self) -> tuple[Dict[str, Any], int]:
        """Get all category information."""
        with self.tracker_lock:
            categories = {
                'default': self.tracker.classifier.categories.default_categories,
                'custom': self.tracker.classifier.categories.custom_categories,
                'app_mappings': self.tracker.classifier.categories.app_mappings
            }
        
        return {
            'status': 'success',
            'data': categories
        }, HTTP_OK
    
    def add_custom_category(self) -> tuple[Dict[str, Any], int]:
        """Add a new custom category."""
        data = request.get_json()
        category_name = data.get('name')
        patterns = data.get('patterns')
        
        # Validate input
        validation_error = self._validate_category_input(category_name, patterns)
        if validation_error:
            return validation_error
        
        with self.tracker_lock:
            self.tracker.classifier.categories.add_category(category_name, patterns)
        
        logger.info(f"Added custom category: {category_name} with patterns {patterns}")
        return {
            'status': 'success',
            'message': f"Custom category '{category_name}' added successfully."
        }, HTTP_CREATED
    
    def delete_custom_category(self, category_name: str) -> tuple[Dict[str, Any], int]:
        """Delete a custom category."""
        with self.tracker_lock:
            if not self.tracker.classifier.categories.remove_custom_category(category_name):
                return {
                    'status': 'error',
                    'message': f"Custom category '{category_name}' not found."
                }, HTTP_NOT_FOUND
        
        logger.info(f"Deleted custom category: {category_name}")
        return {
            'status': 'success',
            'message': f"Custom category '{category_name}' deleted successfully."
        }, HTTP_OK
    
    def map_application_to_category(self) -> tuple[Dict[str, Any], int]:
        """Map an application to a category."""
        data = request.get_json()
        app_name = data.get('app_name')
        category = data.get('category')
        
        if not app_name or not category:
            return {
                'status': 'error',
                'message': 'Invalid input. "app_name" (string) and "category" (string) are required.'
            }, HTTP_BAD_REQUEST
        
        with self.tracker_lock:
            self.tracker.classifier.categories.map_app(app_name, category)
        
        logger.info(f"Mapped app '{app_name}' to category '{category}'")
        return {
            'status': 'success',
            'message': f"Application '{app_name}' mapped to category '{category}' successfully."
        }, HTTP_CREATED
    
    def unmap_application_from_category(self) -> tuple[Dict[str, Any], int]:
        """Remove application category mapping."""
        data = request.get_json()
        app_name = data.get('app_name')
        
        if not app_name:
            return {
                'status': 'error',
                'message': 'Invalid input. "app_name" (string) is required.'
            }, HTTP_BAD_REQUEST
        
        with self.tracker_lock:
            if not self.tracker.classifier.categories.unmap_app(app_name):
                return {
                    'status': 'error',
                    'message': f"Application mapping for '{app_name}' not found."
                }, HTTP_NOT_FOUND
        
        logger.info(f"Unmapped app: {app_name}")
        return {
            'status': 'success',
            'message': f"Application '{app_name}' unmapped successfully."
        }, HTTP_OK
    
    def _validate_category_input(self, category_name, patterns) -> tuple[Dict[str, Any], int] | None:
        """Validate category input parameters."""
        if (not category_name or 
            not isinstance(patterns, list) or 
            not all(isinstance(p, str) for p in patterns)):
            return {
                'status': 'error',
                'message': 'Invalid input. "name" (string) and "patterns" (list of strings) are required.'
            }, HTTP_BAD_REQUEST
        return None