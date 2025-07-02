import re
from typing import Dict, List, Optional
from ..Storage.category_storage import CategoryStorage

class Categories:
    def __init__(self):
        self.storage = CategoryStorage()
        self._load_categories()
    
    def _load_categories(self):
        """Load categories from storage"""
        self.default_categories = {
            'search': [r'search', r'find', r'cortana'],
            # ... other default categories ...
        }
        self.custom_categories = self.storage.load_custom_categories()
        self.app_mappings = self.storage.load_app_mappings()
    
    def get_mapped_category(self, process_name: str, title: str, class_name: str) -> Optional[str]:
        """Check if app is directly mapped to a category"""
        lower_process = process_name.lower()
        lower_title = title.lower()
        
        for app_pattern, category in self.app_mappings.items():
            if (app_pattern in lower_process or 
                app_pattern in lower_title):
                return category
        return None
    
    def match_patterns(self, title: str, class_name: str, process_name: str) -> str:
        """Match window against category patterns"""
        # Combine default and custom categories
        all_categories = {**self.default_categories, **self.custom_categories}
        
        for category, patterns in all_categories.items():
            if self._matches_any_pattern(patterns, title, class_name, process_name):
                return category
        return 'application'
    
    def _matches_any_pattern(self, patterns: List[str], *texts: str) -> bool:
        """Check if any pattern matches any of the texts"""
        for text in texts:
            if not text:
                continue
            lower_text = text.lower()
            for pattern in patterns:
                if re.search(pattern, lower_text):
                    return True
        return False
    
    # Category management API
    def add_category(self, name: str, patterns: List[str]):
        """Add a new custom category"""
        self.custom_categories[name] = patterns
        self.storage.save_custom_categories(self.custom_categories)
    
    def map_app(self, app_name: str, category: str):
        """Map an app to a category"""
        self.app_mappings[app_name.lower()] = category
        self.storage.save_app_mappings(self.app_mappings)
    
    # ... other category management methods ...

    def remove_custom_category(self, name: str) -> bool:
        """Remove a custom category."""
        if name in self.custom_categories:
            del self.custom_categories[name]
            self.storage.save_custom_categories(self.custom_categories)
            return True
        return False

    def unmap_app(self, app_name: str) -> bool:
        """Remove an app mapping."""
        lower_app_name = app_name.lower()
        if lower_app_name in self.app_mappings:
            del self.app_mappings[lower_app_name]
            self.storage.save_app_mappings(self.app_mappings)
            return True
        return False