from PyQt6.QtCore import QThread, pyqtSignal
from pynput.mouse import Button
from pynput.keyboard import Key
import time

class ReplayThread(QThread):
    status_update = pyqtSignal(str)
    
    def __init__(self, actions, mouse, keyboard):
        super().__init__()
        self.actions = actions
        self.mouse = mouse
        self.keyboard = keyboard
        self.pressed_keys = set()
    
    def run(self):
        self.status_update.emit("Playing...")
        last_time = 0
        
        for action in self.actions:
            time_diff = action['time'] - last_time
            if time_diff > 0:
                time.sleep(time_diff)
            
            if action['type'] == 'move':
                self.mouse.position = (action['x'], action['y'])
            elif action['type'] == 'click':
                self.mouse.position = (action['x'], action['y'])
                button = eval(f"Button.{action['button'].split('.')[-1]}")
                if action['pressed']:
                    self.mouse.press(button)
                else:
                    self.mouse.release(button)
            elif action['type'] == 'key_press':
                try:
                    key_str = action['key']
                    if key_str not in self.pressed_keys:
                        if key_str.startswith('Key.'):
                            key = eval(f"Key.{key_str.split('.')[-1]}")
                            self.keyboard.press(key)
                        else:
                            self.keyboard.press(key_str)
                        self.pressed_keys.add(key_str)
                except:
                    pass
            elif action['type'] == 'key_release':
                try:
                    key_str = action['key']
                    if key_str in self.pressed_keys:
                        if key_str.startswith('Key.'):
                            key = eval(f"Key.{key_str.split('.')[-1]}")
                            self.keyboard.release(key)
                        else:
                            self.keyboard.release(key_str)
                        self.pressed_keys.remove(key_str)
                except:
                    pass
            
            last_time = action['time']
        
        # Release all pressed keys
        for key_str in list(self.pressed_keys):
            try:
                if key_str.startswith('Key.'):
                    key = eval(f"Key.{key_str.split('.')[-1]}")
                    self.keyboard.release(key)
                else:
                    self.keyboard.release(key_str)
            except:
                pass
        self.pressed_keys.clear()
        
        self.status_update.emit("Ready\nPress 'R' to record") 