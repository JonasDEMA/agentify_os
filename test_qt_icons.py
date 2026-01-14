"""Test Qt emoji icons."""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from agents.desktop_rpa.ui.qt_icon_loader import get_emoji_icon, get_status_icon


class TestWindow(QMainWindow):
    """Test window for emoji icons."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎨 Qt Emoji Icon Test")
        self.setGeometry(100, 100, 600, 400)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("Testing Colorful Emoji Icons in PySide6")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Test emoji icons
        emoji_layout = QHBoxLayout()
        
        emojis = [
            ('search', '🔍 Search'),
            ('list', '📋 List'),
            ('edit', '✏️ Edit'),
            ('play', '▶️ Play'),
            ('stop', '⏹️ Stop'),
            ('chart', '📊 Chart'),
            ('eye', '👁️ Eye'),
            ('book', '📚 Book'),
        ]
        
        for icon_name, text in emojis:
            btn = QPushButton(text)
            btn.setIcon(get_emoji_icon(icon_name, 24))
            btn.setIconSize(btn.sizeHint())
            emoji_layout.addWidget(btn)
        
        layout.addLayout(emoji_layout)
        
        # Test status icons
        status_layout = QHBoxLayout()
        
        statuses = [
            ('#4CAF50', '🟢 Green'),
            ('#FF9800', '🟡 Orange'),
            ('#F44336', '🔴 Red'),
            ('#2196F3', '🔵 Blue'),
            ('#9C27B0', '🟣 Purple'),
            ('#9E9E9E', '⚪ Gray'),
        ]
        
        for color, text in statuses:
            label = QLabel(text)
            label.setStyleSheet(f"font-size: 14px; padding: 5px; background-color: {color}20; border-radius: 5px;")
            status_layout.addWidget(label)
        
        layout.addLayout(status_layout)
        
        # Info
        info = QLabel("✅ If you see colorful emojis above, PySide6 is rendering them correctly!")
        info.setStyleSheet("font-size: 14px; margin: 20px; color: green;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        layout.addStretch()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

