class AppStyles:
    MAIN_WINDOW = """
        QMainWindow, QWidget {
            background-color: #f0f0f0;
        }
    """
    
    RECORD_BUTTON = """
        QPushButton#recordButton {
            background-color: #2ecc71;
            color: white;
            border: none;
            padding: 15px;  
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            min-width: 200px;
            margin: 10px;
        }
        QPushButton#recordButton:hover {
            background-color: #27ae60;
        }
        QPushButton#recordButton[recording="true"] {
            background-color: #e74c3c;
        }
        QPushButton#recordButton[recording="true"]:hover {
            background-color: #c0392b;
        }
    """
    
    FAVORITE_BUTTON = """
        QPushButton#favoriteButton {
            background-color: #f1c40f;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            min-width: 100px;
        }
        QPushButton#favoriteButton:hover {
            background-color: #f39c12;
        }
    """
    
    FAVORITES_BUTTON = """
        QPushButton#favoritesButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            min-width: 100px;
        }
        QPushButton#favoritesButton:hover {
            background-color: #2980b9;
        }
    """
    
    LABELS = """
        QLabel {
            color: #2c3e50;
            background: transparent;
        }
        QLabel#titleLabel {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background: transparent;
        }
        QLabel#statusLabel {
            color: #34495e;
            font-size: 13px;
            background: transparent;
        }
        QLabel#infoLabel {
            color: #7f8c8d;
            font-size: 11px;
            background: transparent;
        }
    """
    
    FRAMES = """
        QFrame#optionsFrame, QFrame#statusFrame {
            background-color: #f0f0f0;
            border: none;
            border-radius: 10px;
            padding: 15px;
            margin: 5px;
        }
    """
    
    CHECKBOXES = """
        QCheckBox {
            spacing: 10px;
            color: #2c3e50;
            padding: 5px;
            background: transparent;
            font-size: 13px;
        }
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
            border-radius: 4px;
            border: 2px solid #95a5a6;
            background-color: transparent;
        }
        QCheckBox::indicator:checked {
            border: none;
            background-color: #2ecc71;
        }
        QCheckBox::indicator:unchecked {
            background-color: transparent;
        }
        QCheckBox::indicator:hover {
            border-color: #2ecc71;
        }
    """
    
    @classmethod
    def get_all_styles(cls):
        return (cls.MAIN_WINDOW + cls.RECORD_BUTTON + cls.FAVORITE_BUTTON + 
                cls.FAVORITES_BUTTON + cls.LABELS + cls.FRAMES + cls.CHECKBOXES) 