from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from pynput import keyboard

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Settings")
        self.setFixedSize(300, 250)
        
        self.setup_ui()
        self.setup_styles()
        
        # Key detection variables
        self.current_button = None
        self.key_combination = []
        self.listening_for_keys = False
        
        # Show current shortcuts
        self.update_button_texts()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Shortcut Keys")
        title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Record shortcut
        record_layout = QHBoxLayout()
        record_label = QLabel("Record:")
        self.record_input = QPushButton("Waiting for key...")
        self.record_input.setFixedHeight(35)
        self.record_input.clicked.connect(lambda: self.start_key_detection(self.record_input))
        record_layout.addWidget(record_label)
        record_layout.addWidget(self.record_input)
        layout.addLayout(record_layout)
        
        # Replay shortcut
        replay_layout = QHBoxLayout()
        replay_label = QLabel("Play:")
        self.replay_input = QPushButton("Waiting for key...")
        self.replay_input.setFixedHeight(35)
        self.replay_input.clicked.connect(lambda: self.start_key_detection(self.replay_input))
        replay_layout.addWidget(replay_label)
        replay_layout.addWidget(self.replay_input)
        layout.addLayout(replay_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.reset_settings)
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(reset_button)
        button_layout.addWidget(save_button)
        layout.addLayout(button_layout)
        
    def setup_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                background-color: #ffffff;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                text-align: left;
            }
            QPushButton:hover {
                border-color: #3498db;
            }
            QPushButton[listening="true"] {
                background-color: #e8f5e9;
                border-color: #2ecc71;
            }
            QPushButton#saveButton, QPushButton#resetButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                text-align: center;
            }
            QPushButton#resetButton {
                background-color: #e74c3c;
            }
            QPushButton#saveButton:hover {
                background-color: #27ae60;
            }
            QPushButton#resetButton:hover {
                background-color: #c0392b;
            }
        """)
        
    def update_button_texts(self):
        self.record_input.setText(self.parent.record_shortcut)
        self.replay_input.setText(self.parent.replay_shortcut)
        
    def start_key_detection(self, button):
        if self.listening_for_keys:
            return
            
        self.listening_for_keys = True
        self.current_button = button
        self.key_combination = []
        button.setProperty("listening", True)
        button.setText("Press key combination...")
        button.style().unpolish(button)
        button.style().polish(button)
        
        self.key_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.key_listener.start()
        
    def on_key_press(self, key):
        if not self.listening_for_keys:
            return
            
        try:
            key_str = key.char
        except AttributeError:
            key_str = str(key).replace('Key.', '')
            
        if key_str not in self.key_combination:
            self.key_combination.append(key_str)
            self.current_button.setText('+'.join(self.key_combination))
            
    def on_key_release(self, key):
        if not self.listening_for_keys:
            return
            
        self.listening_for_keys = False
        if self.key_listener:
            self.key_listener.stop()
            
        self.current_button.setProperty("listening", False)
        self.current_button.style().unpolish(self.current_button)
        self.current_button.style().polish(self.current_button)
        
    def reset_settings(self):
        self.parent.record_shortcut = "r"
        self.parent.replay_shortcut = "s"
        self.update_button_texts()
        
        if self.parent.hotkey_listener:
            self.parent.hotkey_listener.stop()
        self.parent.hotkey_listener = keyboard.Listener(
            on_press=self.parent.on_key_press,
            on_release=self.parent.on_key_release
        )
        self.parent.hotkey_listener.start()
        
        self.parent.save_settings()
        self.parent.update_shortcut_status()
        QMessageBox.information(self, "Info", "Shortcut keys have been reset!")
        
    def save_settings(self):
        record_key = self.record_input.text().lower()
        replay_key = self.replay_input.text().lower()
        
        if not record_key or not replay_key or record_key == "waiting for key..." or replay_key == "waiting for key...":
            QMessageBox.critical(self, "Error", "Please set all shortcut keys!")
            return
            
        if record_key == replay_key:
            QMessageBox.critical(self, "Error", "Shortcut keys cannot be the same!")
            return
            
        self.parent.record_shortcut = record_key
        self.parent.replay_shortcut = replay_key
        self.parent.save_settings()
        self.close() 