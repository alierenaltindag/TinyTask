import json
import os

class Settings:
    def __init__(self):
        self.track_mouse = True
        self.track_keyboard = True
        self.record_key = 'ctrl+s'
        self.replay_key = 'ctrl+r'
        self.settings_file = 'macro_settings.json'
        
    def save(self):
        settings = {
            'track_mouse': self.track_mouse,
            'track_keyboard': self.track_keyboard,
            'record_key': self.record_key,
            'replay_key': self.replay_key
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)
            
    def load(self):
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.track_mouse = settings.get('track_mouse', True)
                self.track_keyboard = settings.get('track_keyboard', True)
                self.record_key = settings.get('record_key', 'ctrl+s')
                self.replay_key = settings.get('replay_key', 'ctrl+r')
        except FileNotFoundError:
            # Use default values if file doesn't exist
            pass 