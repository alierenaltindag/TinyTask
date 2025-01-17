import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QCheckBox, QLabel, QFrame, QMessageBox,
                            QInputDialog, QDialog, QApplication)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
import time

from ui.styles.app_styles import AppStyles
from ui.dialogs.settings_dialog import SettingsDialog
from ui.dialogs.favorites_dialog import FavoritesDialog
from utils.file_handler import FileHandler
from utils.replay_thread import ReplayThread
from models.settings import Settings

class MacroRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro Recorder")
        self.setFixedSize(350, 650)
        
        # Initialize controllers
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.recording = False
        self.is_replaying = False
        self.actions = []
        self.start_time = 0
        self.active_macro_name = None
        self.active_keys = []
        
        # Load settings
        self.settings = Settings()
        self.settings.load()
        self.record_shortcut = self.settings.record_key
        self.replay_shortcut = self.settings.replay_key
        
        # Dialog references
        self.settings_dialog = None
        self.favorites_dialog = None
        
        self.setup_ui()
        self.setup_icon()
        self.setup_listeners()
        self.update_shortcut_status()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Macro Recorder")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        settings_button = QPushButton()
        settings_button.setObjectName("settingsButton")
        settings_button.setIcon(QIcon.fromTheme("configure"))
        settings_button.setFixedSize(32, 32)
        settings_button.clicked.connect(self.show_settings)
        header_layout.addWidget(settings_button, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(header_layout)
        
        # Record Button
        self.record_button = QPushButton("Start Recording")
        self.record_button.setObjectName("recordButton")
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Favorite buttons
        buttons_layout = QHBoxLayout()
        self.favorite_button = QPushButton("Add to Favorites")
        self.favorite_button.setObjectName("favoriteButton")
        self.favorite_button.clicked.connect(self.add_to_favorites)
        buttons_layout.addWidget(self.favorite_button)
        
        self.favorites_button = QPushButton("My Favorites")
        self.favorites_button.setObjectName("favoritesButton")
        self.favorites_button.clicked.connect(self.show_favorites)
        buttons_layout.addWidget(self.favorites_button)
        layout.addLayout(buttons_layout)
        
        # Options Frame
        options_frame = QFrame()
        options_frame.setObjectName("optionsFrame")
        options_layout = QVBoxLayout(options_frame)
        
        options_title = QLabel("Tracking Options")
        options_title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        options_layout.addWidget(options_title)
        
        self.track_mouse_var = QCheckBox("Track Mouse Movements")
        self.track_keyboard_var = QCheckBox("Track Keyboard Keys")
        
        self.track_mouse_var.setChecked(self.settings.track_mouse)
        self.track_keyboard_var.setChecked(self.settings.track_keyboard)
        
        self.track_mouse_var.stateChanged.connect(self.save_settings)
        self.track_keyboard_var.stateChanged.connect(self.save_settings)
        
        options_layout.addWidget(self.track_mouse_var)
        options_layout.addWidget(self.track_keyboard_var)
        layout.addWidget(options_frame)
        
        # Status Frame
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QVBoxLayout(status_frame)
        
        status_title = QLabel("Status")
        status_title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        status_layout.addWidget(status_title)
        
        self.status_label = QLabel("Ready\nPress 'R' to record")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        self.active_macro_label = QLabel()
        self.active_macro_label.setObjectName("statusLabel")
        self.active_macro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.active_macro_label)
        
        layout.addWidget(status_frame)
        
        # Apply styles
        self.setStyleSheet(AppStyles.get_all_styles())
        
    def setup_icon(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        
        icon_path = os.path.join(base_path, "resources", "icons", "icon.svg")
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.setWindowIcon(icon)
            app = QApplication.instance()
            app.setWindowIcon(icon)
            
    def setup_listeners(self):
        self.mouse_listener = None
        self.keyboard_listener = None
        self.hotkey_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.hotkey_listener.start()
        
    def toggle_recording(self):
        if not self.recording and not (self.track_mouse_var.isChecked() or self.track_keyboard_var.isChecked()):
            QMessageBox.critical(self, "Error", "At least one tracking option must be enabled!")
            return
            
        self.recording = not self.recording
        
        if self.recording:
            self.active_macro_name = None
            self.active_macro_label.setText("")
            self.record_button.setText("Stop Recording")
            self.record_button.setProperty("recording", True)
            self.status_label.setText(f"Recording...\nPress '{self.record_shortcut.upper()}' again to stop")
            self.actions = []
            self.start_time = time.time()
            
            if self.track_mouse_var.isChecked():
                self.mouse_listener = mouse.Listener(
                    on_move=self.on_move,
                    on_click=self.on_click
                )
                self.mouse_listener.start()
            
            if self.track_keyboard_var.isChecked():
                self.keyboard_listener = keyboard.Listener(
                    on_press=self.on_key_press,
                    on_release=self.on_key_release
                )
                self.keyboard_listener.start()
        else:
            self.record_button.setText("Start Recording")
            self.record_button.setProperty("recording", False)
            self.update_shortcut_status()
            
            if self.mouse_listener:
                self.mouse_listener.stop()
            if self.keyboard_listener:
                self.keyboard_listener.stop()
            
            FileHandler.save_macro(self.actions)
        
        self.record_button.style().unpolish(self.record_button)
        self.record_button.style().polish(self.record_button)
        
    def on_move(self, x, y):
        if self.recording and self.track_mouse_var.isChecked():
            current_time = time.time() - self.start_time
            self.actions.append({
                'type': 'move',
                'x': x,
                'y': y,
                'time': current_time
            })
    
    def on_click(self, x, y, button, pressed):
        if self.recording:
            button_pos = self.record_button.mapToGlobal(self.record_button.rect().topLeft())
            button_rect = self.record_button.rect()
            
            if not (button_pos.x() <= x <= button_pos.x() + button_rect.width() and 
                   button_pos.y() <= y <= button_pos.y() + button_rect.height()):
                current_time = time.time() - self.start_time
                self.actions.append({
                    'type': 'click',
                    'x': x,
                    'y': y,
                    'button': str(button),
                    'pressed': pressed,
                    'time': current_time
                })
    
    def on_key_press(self, key):
        if self.settings_dialog and self.settings_dialog.isVisible():
            return
            
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key).replace('Key.', '')
            
        if key_char not in self.active_keys:
            self.active_keys.append(key_char)
            current_combination = '+'.join(sorted(self.active_keys))
            
            if current_combination == self.record_shortcut.lower():
                self.toggle_recording()
                return
            elif current_combination == self.replay_shortcut.lower():
                self.replay_macro()
                return
                
            if self.recording and self.track_keyboard_var.isChecked():
                current_time = time.time() - self.start_time
                try:
                    key_data = key.char if hasattr(key, 'char') else str(key)
                except AttributeError:
                    key_data = str(key)
                    
                self.actions.append({
                    'type': 'key_press',
                    'key': key_data,
                    'time': current_time
                })
    
    def on_key_release(self, key):
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key).replace('Key.', '')
            
        if self.recording and self.track_keyboard_var.isChecked() and key_char in self.active_keys:
            current_time = time.time() - self.start_time
            try:
                key_data = key.char if hasattr(key, 'char') else str(key)
            except AttributeError:
                key_data = str(key)
                
            self.actions.append({
                'type': 'key_release',
                'key': key_data,
                'time': current_time
            })
            
        if key_char in self.active_keys:
            self.active_keys.remove(key_char)
            
    def replay_macro(self):
        if self.recording or self.is_replaying:
            return
            
        if self.active_macro_name:
            favorites = FileHandler.load_favorites()
            if self.active_macro_name in favorites:
                self.replay_actions(favorites[self.active_macro_name], self.active_macro_name)
                return
        
        actions = FileHandler.load_macro()
        if actions:
            self.replay_actions(actions)
            
    def replay_actions(self, actions, macro_name=None):
        if self.is_replaying:
            QMessageBox.warning(self, "Warning", "A macro is currently playing!")
            return
            
        self.is_replaying = True
        self.actions = actions
        if macro_name:
            self.active_macro_name = macro_name
            self.active_macro_label.setText(f"Active Macro: {macro_name}")
            
        self.replay_thread = ReplayThread(actions, self.mouse, self.keyboard)
        self.replay_thread.status_update.connect(self.update_status)
        self.replay_thread.finished.connect(self.on_replay_finished)
        self.replay_thread.start()
        self.status_label.setText("Playing...\nPlease wait")
        
    def on_replay_finished(self):
        self.is_replaying = False
        self.update_shortcut_status()
        
    def add_to_favorites(self):
        if not os.path.exists(FileHandler.MACRO_FILE):
            QMessageBox.warning(self, "Warning", "No recorded macro found!")
            return
            
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Favorite Macro")
        dialog.setLabelText("Enter a name for the macro:")
        dialog.setStyleSheet("""
            QInputDialog {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #2c3e50;
                font-size: 12px;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                background-color: #3498db;
                color: white;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.textValue()
            if name:
                macro = FileHandler.load_macro()
                if FileHandler.save_favorite(name, macro):
                    QMessageBox.information(self, "Success", "Macro added to favorites!")
                    # Refresh favorites dialog if it's open
                    if self.favorites_dialog and self.favorites_dialog.isVisible():
                        self.favorites_dialog.load_favorites()
                else:
                    QMessageBox.critical(self, "Error", "Could not save macro!")
                    
    def show_favorites(self):
        if not self.favorites_dialog:
            self.favorites_dialog = FavoritesDialog(self)
        else:
            # Refresh the list when showing the dialog
            self.favorites_dialog.load_favorites()
        self.favorites_dialog.show()
        
    def show_settings(self):
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.show()
        
    def update_status(self, text):
        self.status_label.setText(text)
        
    def update_shortcut_status(self):
        if self.is_replaying:
            self.status_label.setText("Playing...\nPlease wait")
        else:
            status_text = "Ready\n"
            status_text += f"Press '{self.record_shortcut.upper()}' to record\n"
            status_text += f"Press '{self.replay_shortcut.upper()}' to play"
            self.status_label.setText(status_text)
            
    def save_settings(self):
        self.settings.track_mouse = self.track_mouse_var.isChecked()
        self.settings.track_keyboard = self.track_keyboard_var.isChecked()
        self.settings.record_key = self.record_shortcut
        self.settings.replay_key = self.replay_shortcut
        self.settings.save()
        self.update_shortcut_status() 