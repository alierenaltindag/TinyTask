from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QListWidget, QMessageBox)
from PyQt6.QtGui import QFont
from utils.file_handler import FileHandler

class FavoritesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Favorite Macros")
        self.setFixedSize(400, 500)
        
        self.setup_ui()
        self.setup_styles()
        self.load_favorites()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("My Favorite Macros")
        title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Macro list
        self.macro_list = QListWidget()
        layout.addWidget(self.macro_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        play_button = QPushButton("Play")
        play_button.clicked.connect(self.play_selected_macro)
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_selected_macro)
        button_layout.addWidget(play_button)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)
        
    def setup_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #2c3e50;
            }
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #ecf0f1;
                color: #2c3e50;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton[delete="true"] {
                background-color: #e74c3c;
            }
            QPushButton[delete="true"]:hover {
                background-color: #c0392b;
            }
        """)
    
    def load_favorites(self):
        self.macro_list.clear()
        favorites = FileHandler.load_favorites()
        for name in favorites.keys():
            self.macro_list.addItem(name)
    
    def play_selected_macro(self):
        current_item = self.macro_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a macro!")
            return
            
        favorites = FileHandler.load_favorites()
        macro_name = current_item.text()
        if macro_name in favorites:
            self.parent.replay_actions(favorites[macro_name], macro_name)
            self.close()
    
    def delete_selected_macro(self):
        current_item = self.macro_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a macro!")
            return
            
        reply = QMessageBox.question(self, "Confirm", 
                                   "Are you sure you want to delete this macro?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            macro_name = current_item.text()
            if FileHandler.delete_favorite(macro_name):
                self.load_favorites()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete macro!") 