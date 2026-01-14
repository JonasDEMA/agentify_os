"""CPA Agent Monitor - Modern Qt UI with colorful emoji icons."""
import sys
import asyncio
from datetime import datetime
from typing import Any
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QComboBox, QLineEdit, QGroupBox,
    QTableWidget, QTableWidgetItem, QSplitter, QHeaderView
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QFont, QColor

from agents.desktop_rpa.cognitive.cognitive_executor import CognitiveExecutor
from agents.desktop_rpa.ui.qt_icon_loader import get_emoji_icon, get_status_icon


class WorkerSignals(QObject):
    """Signals for worker thread."""
    log = Signal(str, str)  # message, level
    status = Signal(str, str)  # text, color
    event = Signal(dict)  # event data


class CPAMonitorQt(QMainWindow):
    """Modern CPA Agent Monitor with Qt and colorful emojis."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🤖 CPA Agent Monitor - LuminaOS")
        self.setGeometry(100, 100, 1400, 800)
        
        # State
        self.executor: CognitiveExecutor | None = None
        self.is_running = False
        self.templates = self._load_templates()
        self.all_templates = sorted(self.templates.keys())
        
        # Signals
        self.signals = WorkerSignals()
        self.signals.log.connect(self._on_log)
        self.signals.status.connect(self._on_status_change)
        
        # Setup UI
        self._setup_ui()
        
        # Apply dark theme
        self._apply_theme()
    
    def _setup_ui(self):
        """Setup the UI components."""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        
        # Left panel - Control
        left_panel = self._create_control_panel()
        
        # Right panel - Monitor & Learning
        right_panel = self._create_right_panel()
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
    
    def _create_control_panel(self) -> QWidget:
        """Create control panel."""
        panel = QGroupBox("🎮 Control Panel")
        layout = QVBoxLayout(panel)
        
        # Search Templates
        search_label = QLabel("Search Templates:")
        search_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        layout.addWidget(search_label)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Type to search...")
        self.search_box.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_box)

        # Template Selection
        template_label = QLabel("Select Template:")
        template_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        layout.addWidget(template_label)

        self.template_combo = QComboBox()
        self.template_combo.addItems(self.all_templates)
        self.template_combo.currentTextChanged.connect(self._on_template_selected)
        layout.addWidget(self.template_combo)

        # Custom Task
        custom_label = QLabel("Custom Task:")
        custom_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        layout.addWidget(custom_label)
        
        self.task_text = QTextEdit()
        self.task_text.setPlaceholderText("Enter your custom task here...")
        self.task_text.setMaximumHeight(150)
        layout.addWidget(self.task_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Task")
        self.start_btn.setIcon(get_emoji_icon('play', 20))
        self.start_btn.clicked.connect(self._start_task)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setIcon(get_emoji_icon('stop', 20))
        self.stop_btn.clicked.connect(self._stop_task)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        button_layout.addWidget(self.stop_btn)
        
        layout.addLayout(button_layout)
        
        # Status
        status_label = QLabel("Status:")
        status_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        layout.addWidget(status_label)

        self.status_label = QLabel("Idle")
        self.status_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.status_label.setStyleSheet("color: gray; padding: 5px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create right panel with monitor and learning."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Monitor Panel
        monitor_group = QGroupBox("Live Monitoring")
        monitor_layout = QVBoxLayout(monitor_group)

        # Current Goal
        goal_layout = QHBoxLayout()
        goal_layout.addWidget(QLabel("Current Goal:"))
        self.goal_label = QLabel("None")
        self.goal_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        goal_layout.addWidget(self.goal_label)
        goal_layout.addStretch()
        monitor_layout.addLayout(goal_layout)

        # Activity Log
        log_label = QLabel("Activity Log:")
        log_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        monitor_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(300)
        monitor_layout.addWidget(self.log_text)
        
        layout.addWidget(monitor_group)
        
        # Learning History
        learning_group = QGroupBox("Learning History")
        learning_layout = QVBoxLayout(learning_group)

        self.learning_table = QTableWidget()
        self.learning_table.setColumnCount(4)
        self.learning_table.setHorizontalHeaderLabels(["Time", "Task", "Strategy", "Score"])
        self.learning_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        learning_layout.addWidget(self.learning_table)
        
        layout.addWidget(learning_group)
        
        return panel
    
    def _load_templates(self) -> dict[str, str]:
        """Load task templates."""
        return {
            "Browser": "Open the default web browser",
            "Calculator": "Find and open the Calculator application",
            "File Explorer": "Open Windows File Explorer",
            "Notepad": "Open Notepad application from the Start Menu",
            "Ransomware Protection": "Activate Ransomware Protection in Windows Security",
            "Screenshot": "Take a screenshot of the current desktop",
            "Search Control Panel": "Open Start Menu and search for 'Control Panel'",
            "Start Menu": "Open the Windows Start Menu by clicking the Start button",
            "Type in Notepad": "Open Notepad and type 'Hello from CPA Agent!'",
        }
    
    def _on_search_changed(self, text: str):
        """Handle search text change."""
        search_text = text.lower()
        
        if not search_text:
            self.template_combo.clear()
            self.template_combo.addItems(self.all_templates)
        else:
            filtered = [t for t in self.all_templates if search_text in t.lower()]
            self.template_combo.clear()
            self.template_combo.addItems(filtered)
    
    def _on_template_selected(self, template_name: str):
        """Handle template selection."""
        if template_name in self.templates:
            self.task_text.setPlainText(self.templates[template_name])
    
    def _start_task(self):
        """Start executing a task."""
        task_goal = self.task_text.toPlainText().strip()
        if not task_goal:
            self._log("⚠️ Please enter a task goal!", "warning")
            return
        
        self.is_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.goal_label.setText(task_goal)
        self._update_status("Running", "#4CAF50")

        self._log(f"Starting task: {task_goal}", "info")
        
        # TODO: Run task in background thread with asyncio
    
    def _stop_task(self):
        """Stop current task."""
        self.is_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._update_status("Stopped", "#FF9800")
        self._log("Task stopped by user", "warning")
    
    def _log(self, message: str, level: str = "info"):
        """Add log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Icon mapping
        icon_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "thinking": "💭",
        }

        color_map = {
            "info": "#2196F3",
            "success": "#4CAF50",
            "warning": "#FF9800",
            "error": "#F44336",
            "thinking": "#9C27B0",
        }

        icon = icon_map.get(level, "•")
        color = color_map.get(level, "#FFFFFF")

        html = f'<span style="color: gray;">[{timestamp}]</span> {icon} <span style="color: {color};">{message}</span><br>'
        self.log_text.insertHtml(html)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def _update_status(self, text: str, color: str):
        """Update status label."""
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; padding: 5px; font-weight: bold;")
    
    def _on_log(self, message: str, level: str):
        """Handle log signal."""
        self._log(message, level)
    
    def _on_status_change(self, text: str, color: str):
        """Handle status change signal."""
        self._update_status(text, color)
    
    def _apply_theme(self):
        """Apply dark theme."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #3f3f3f;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #3f3f3f;
                border-radius: 3px;
                padding: 5px;
                color: #ffffff;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #2196F3;
            }
            QTableWidget {
                background-color: #2d2d2d;
                border: 1px solid #3f3f3f;
                gridline-color: #3f3f3f;
            }
            QHeaderView::section {
                background-color: #3f3f3f;
                color: #ffffff;
                padding: 5px;
                border: none;
            }
            QLabel {
                background-color: transparent;
            }
        """)


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = CPAMonitorQt()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

