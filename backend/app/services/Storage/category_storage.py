import json
from pathlib import Path
from typing import Dict, List

class CategoryStorage:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "window_tracker"
        self.categories_file = self.config_dir / "categories.json"
        self._ensure_config_dir_exists()
    
    def _ensure_config_dir_exists(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_custom_categories(self) -> Dict[str, List[str]]:
        try:
            if self.categories_file.exists():
                with open(self.categories_file, 'r') as f:
                    data = json.load(f)
                    return data.get('categories', {})
        except Exception:
            return {}
    
    def load_app_mappings(self) -> Dict[str, str]:
        try:
            if self.categories_file.exists():
                with open(self.categories_file, 'r') as f:
                    data = json.load(f)
                    return data.get('app_mappings', {})
        except Exception:
            return {}
    
    def save_custom_categories(self, categories: Dict[str, List[str]]):
        self._save_data({'categories': categories})
    
    def save_app_mappings(self, mappings: Dict[str, str]):
        self._save_data({'app_mappings': mappings})
    
    def _save_data(self, data: dict):
        try:
            # Load existing data first
            existing = {}
            if self.categories_file.exists():
                with open(self.categories_file, 'r') as f:
                    existing = json.load(f)
            
            # Update with new data
            existing.update(data)
            
            # Save back to file
            with open(self.categories_file, 'w') as f:
                json.dump(existing, f, indent=2)
        except Exception as e:
            print(f"Error saving category data: {e}")