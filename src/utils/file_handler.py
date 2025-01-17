import json
import os

class FileHandler:
    MACRO_FILE = 'macro.json'
    FAVORITES_FILE = 'favorite_macros.json'
    
    @classmethod
    def save_macro(cls, actions):
        """Save the current macro to file."""
        if actions:
            with open(cls.MACRO_FILE, 'w') as f:
                json.dump(actions, f)
                
    @classmethod
    def load_macro(cls):
        """Load the current macro from file."""
        if os.path.exists(cls.MACRO_FILE):
            with open(cls.MACRO_FILE, 'r') as f:
                return json.load(f)
        return []
    
    @classmethod
    def save_favorite(cls, name, actions):
        """Save a macro to favorites."""
        try:
            favorites = cls.load_favorites()
            favorites[name] = actions
            with open(cls.FAVORITES_FILE, 'w') as f:
                json.dump(favorites, f)
            return True
        except Exception as e:
            print(f"Error saving favorite: {str(e)}")
            return False
            
    @classmethod
    def load_favorites(cls):
        """Load all favorite macros."""
        try:
            with open(cls.FAVORITES_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
            
    @classmethod
    def delete_favorite(cls, name):
        """Delete a favorite macro."""
        try:
            favorites = cls.load_favorites()
            if name in favorites:
                del favorites[name]
                with open(cls.FAVORITES_FILE, 'w') as f:
                    json.dump(favorites, f)
                return True
        except Exception as e:
            print(f"Error deleting favorite: {str(e)}")
        return False 