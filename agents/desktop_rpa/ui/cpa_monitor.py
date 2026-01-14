"""CPA Agent Monitor - Windows UI for monitoring and controlling the Cognitive RPA Agent."""

import asyncio
import json
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import scrolledtext, ttk
from typing import Any

from agents.desktop_rpa.cognitive.cognitive_executor import CognitiveExecutor
from agents.desktop_rpa.ui.onboarding_wizard import check_and_run_onboarding
from agents.desktop_rpa.ui.icon_generator import get_icon


class CPAMonitor:
    """Main UI for CPA Agent Monitoring."""

    def __init__(self):
        """Initialize the monitor UI."""
        self.root = tk.Tk()
        self.root.title("🤖 CPA Agent Monitor - LuminaOS")

        # Config file for window position/size
        self.config_file = Path("ui_config.json")

        # State
        self.executor: CognitiveExecutor | None = None
        self.current_task: dict[str, Any] | None = None
        self.is_running = False
        self.learning_history: list[dict[str, Any]] = []

        # Load icons
        self.icons = {
            'gear': get_icon('gear', 16),
            'search': get_icon('search', 16),
            'list': get_icon('list', 16),
            'edit': get_icon('edit', 16),
            'play': get_icon('play', 16),
            'stop': get_icon('stop', 16),
            'chart': get_icon('chart', 16),
            'eye': get_icon('eye', 16),
            'book': get_icon('book', 16),
            'circle_green': get_icon('circle_green', 12),
            'circle_orange': get_icon('circle_orange', 12),
            'circle_red': get_icon('circle_red', 12),
            'circle_blue': get_icon('circle_blue', 12),
            'circle_purple': get_icon('circle_purple', 12),
            'circle_gray': get_icon('circle_gray', 12),
        }

        # Load templates
        self.templates = self._load_templates()

        # Load and apply window geometry
        self._load_window_geometry()

        # Setup UI
        self._setup_ui()

        # Bind window close event to save geometry
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Start update loop
        self._schedule_update()
    
    def _setup_ui(self):
        """Setup the UI components."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights - left side wider for templates, right side for monitoring
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=2)  # Left panel - wider for templates (2x)
        main_frame.columnconfigure(1, weight=3)  # Right panel - monitoring (3x)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left Panel - Control
        self._setup_control_panel(main_frame)
        
        # Right Panel - Monitoring
        self._setup_monitor_panel(main_frame)
        
        # Bottom Panel - Learning History
        self._setup_learning_panel(main_frame)
    
    def _setup_control_panel(self, parent):
        """Setup control panel."""
        control_frame = ttk.LabelFrame(parent, text="Control Panel", padding="10")
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))

        # Template selection with search
        search_label = ttk.Label(control_frame, text=" Search Templates:", font=("Segoe UI", 9), image=self.icons['search'], compound=tk.LEFT)
        search_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        ttk.Label(control_frame, text="� Search Templates:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # Search box
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_changed)
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=40, font=("Segoe UI", 10))
        search_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Label(control_frame, text="📋 Select Template:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky=tk.W, pady=(10, 5))

        # Template dropdown
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(control_frame, textvariable=self.template_var, width=40, font=("Segoe UI", 10))

        # Sort templates alphabetically
        sorted_templates = sorted(self.templates.keys())
        self.template_combo['values'] = sorted_templates
        self.all_templates = sorted_templates  # Keep reference for search

        self.template_combo.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.template_combo.bind('<<ComboboxSelected>>', self._on_template_selected)

        # Custom prompt
        ttk.Label(control_frame, text="✏ Custom Task:", font=("Segoe UI", 9)).grid(row=4, column=0, sticky=tk.W, pady=(10, 5))

        self.task_text = scrolledtext.ScrolledText(control_frame, width=45, height=6, wrap=tk.WORD, font=("Segoe UI", 10))
        self.task_text.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        self.start_btn = ttk.Button(button_frame, text="▶ Start Task", command=self._start_task)
        self.start_btn.grid(row=0, column=0, padx=(0, 5))

        self.stop_btn = ttk.Button(button_frame, text="■ Stop", command=self._stop_task, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1)

        # Status
        ttk.Label(control_frame, text="📊 Status:", font=("Segoe UI", 9)).grid(row=7, column=0, sticky=tk.W, pady=(20, 5))

        self.status_label = ttk.Label(control_frame, text="○ Idle", font=("Segoe UI", 10, "bold"), foreground="gray")
        self.status_label.grid(row=8, column=0, sticky=tk.W)
    
    def _setup_monitor_panel(self, parent):
        """Setup monitoring panel."""
        monitor_frame = ttk.LabelFrame(parent, text="👁 Live Monitoring", padding="10")
        monitor_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Current task info
        info_frame = ttk.Frame(monitor_frame)
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(info_frame, text="🎯 Current Goal:").grid(row=0, column=0, sticky=tk.W)
        self.goal_label = ttk.Label(info_frame, text="None", wraplength=500)
        self.goal_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(info_frame, text="📍 Step:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.step_label = ttk.Label(info_frame, text="0/0")
        self.step_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        ttk.Label(info_frame, text="🔍 State:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.state_label = ttk.Label(info_frame, text="N/A")
        self.state_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Activity log
        ttk.Label(monitor_frame, text="📝 Activity Log:").grid(row=1, column=0, sticky=tk.W, pady=(10, 5))

        self.log_text = scrolledtext.ScrolledText(monitor_frame, width=80, height=25, wrap=tk.WORD)
        self.log_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        monitor_frame.rowconfigure(2, weight=1)  # Log expands vertically
        self.log_text.config(state=tk.DISABLED)
        
        # Configure tags for colored text
        self.log_text.tag_config("info", foreground="blue")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("thinking", foreground="purple")
    
    def _setup_learning_panel(self, parent):
        """Setup learning history panel."""
        learning_frame = ttk.LabelFrame(parent, text="📚 Learning History", padding="10")
        learning_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))

        # Treeview for learning history
        columns = ("timestamp", "task", "strategy", "confidence")
        self.learning_tree = ttk.Treeview(learning_frame, columns=columns, show="headings", height=8)

        self.learning_tree.heading("timestamp", text="⏰ Time")
        self.learning_tree.heading("task", text="🎯 Task")
        self.learning_tree.heading("strategy", text="� Strategy")
        self.learning_tree.heading("confidence", text="📊 Score")
        
        self.learning_tree.column("timestamp", width=150)
        self.learning_tree.column("task", width=200)
        self.learning_tree.column("strategy", width=300)
        self.learning_tree.column("confidence", width=100)
        
        self.learning_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(learning_frame, orient=tk.VERTICAL, command=self.learning_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.learning_tree.configure(yscrollcommand=scrollbar.set)
    
    def _load_templates(self) -> dict[str, str]:
        """Load task templates."""
        return {
            "Start Menu": "Open the Windows Start Menu by clicking the Start button",
            "Notepad": "Open Notepad application from the Start Menu",
            "Calculator": "Find and open the Calculator application",
            "File Explorer": "Open Windows File Explorer",
            "Search Control Panel": "Open Start Menu and search for 'Control Panel'",
            "Type in Notepad": "Open Notepad and type 'Hello from CPA Agent!'",
            "Screenshot": "Take a screenshot of the current desktop",
            "Browser": "Open the default web browser",
            "Ransomware Protection": "Activate Ransomware Protection in Windows Security",
        }
    
    def _on_search_changed(self, *args):
        """Handle search text change - filter templates."""
        search_text = self.search_var.get().lower()

        if not search_text:
            # Show all templates if search is empty
            self.template_combo['values'] = self.all_templates
        else:
            # Filter templates that contain search text
            filtered = [t for t in self.all_templates if search_text in t.lower()]
            self.template_combo['values'] = filtered

    def _on_template_selected(self, event):
        """Handle template selection."""
        template_name = self.template_var.get()
        if template_name in self.templates:
            self.task_text.delete("1.0", tk.END)
            self.task_text.insert("1.0", self.templates[template_name])
    
    def _start_task(self):
        """Start executing a task."""
        task_goal = self.task_text.get("1.0", tk.END).strip()
        if not task_goal:
            self._log("⚠ Please enter a task goal!", "warning")
            return

        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="● Running", foreground="green")

        self._log(f"▶ Starting task: {task_goal}", "info")

        # Run task in background thread
        thread = threading.Thread(target=self._run_task_async, args=(task_goal,), daemon=True)
        thread.start()

    def _run_task_async(self, goal: str):
        """Run async task in thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._execute_task(goal))
        finally:
            loop.close()
    
    def _stop_task(self):
        """Stop current task."""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="● Stopped", foreground="orange")
        self._log("■ Task stopped by user", "warning")
    
    def _on_executor_event(self, event: dict):
        """Handle events from the executor."""
        event_type = event.get("type")
        data = event.get("data", {})

        if event_type == "start":
            self._log(f"▶ Starting task: {data.get('goal')}", "info")

        elif event_type == "step":
            step = data.get("step", 0)
            max_steps = data.get("max_steps", 0)
            state = data.get("state", "unknown")
            self.step_label.config(text=f"{step}/{max_steps}")
            self.state_label.config(text=state)

        elif event_type == "screenshot":
            self._log("� Taking screenshot...", "info")

        elif event_type == "thinking":
            message = data.get("message", "Thinking...")
            self._log(f"💭 {message}", "thinking")
            self.status_label.config(text="● Thinking", foreground="purple")

        elif event_type == "vision":
            message = data.get("message", "Detecting UI elements...")
            self._log(f"👁 {message}", "info")
            self.status_label.config(text="● Vision", foreground="blue")

        elif event_type == "action_suggested":
            action = data.get("action", "unknown")
            reasoning = data.get("reasoning", "")
            confidence = data.get("confidence", 0.0)
            confidence_emoji = "●" if confidence >= 0.8 else "◐" if confidence >= 0.6 else "○"
            self._log(f"{confidence_emoji} Suggested: {action.upper()} (confidence: {confidence:.2f})", "info")
            self._log(f"   → {reasoning}", "info")

        elif event_type == "executing":
            action = data.get("action", "unknown")
            self._log(f"⚙ Executing: {action.upper()}", "info")
            self.status_label.config(text=f"● Executing {action}", foreground="green")

        elif event_type == "action_completed":
            result = data.get("result", {})
            status = result.get("status", "unknown")
            if status == "success":
                self._log("✓ Action completed successfully", "success")
            else:
                self._log(f"⚠ Action result: {status}", "warning")

        elif event_type == "completed":
            steps = data.get("steps", 0)
            self._log(f"✓ Task completed in {steps} steps!", "success")
            self.status_label.config(text="● Completed", foreground="green")

    async def _execute_task(self, goal: str):
        """Execute a task using the cognitive executor."""
        try:
            # Create executor with callback and Vision Layer enabled
            self.executor = CognitiveExecutor(callback=self._on_executor_event, use_vision=True)
            self.current_task = {"goal": goal}

            # Execute
            result = await self.executor.execute(self.current_task)

            # Log result
            if result["status"] == "success":
                self._add_learning_entry(goal, result)
            else:
                self._log(f"⚠ Task incomplete: {result.get('final_state', 'unknown')}", "warning")

        except Exception as e:
            self._log(f"✗ Error: {e}", "error")
        finally:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="○ Idle", foreground="gray")
    
    def _add_learning_entry(self, task: str, result: dict[str, Any]):
        """Add entry to learning history."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        strategy = f"{result['steps']} steps"
        confidence = f"{result.get('confidence', 0.85):.2f}"
        
        self.learning_tree.insert("", 0, values=(timestamp, task[:30], strategy, confidence))
        
        # Save to history
        self.learning_history.append({
            "timestamp": timestamp,
            "task": task,
            "result": result,
        })
    
    def _log(self, message: str, tag: str = "info"):
        """Add message to activity log."""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _schedule_update(self):
        """Schedule periodic UI updates."""
        if self.is_running and self.executor:
            # Update current state
            self.goal_label.config(text=self.current_task.get("goal", "N/A"))
            self.state_label.config(text=self.executor.current_state)
            # Note: step count would need to be exposed by executor

        # Schedule next update
        self.root.after(500, self._schedule_update)

    def _load_window_geometry(self):
        """Load window position and size from config file."""
        default_width = 1400
        default_height = 900

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)

                width = config.get('width', default_width)
                height = config.get('height', default_height)
                x = config.get('x')
                y = config.get('y')

                # Check if position is valid (visible on screen)
                if x is not None and y is not None:
                    screen_width = self.root.winfo_screenwidth()
                    screen_height = self.root.winfo_screenheight()

                    # Check if window would be visible
                    if (x >= 0 and y >= 0 and
                        x + width <= screen_width and
                        y + height <= screen_height):
                        # Valid position - use it
                        self.root.geometry(f"{width}x{height}+{x}+{y}")
                        return

                # Invalid or no position - center on screen
                self._center_window(width, height)

            except Exception as e:
                print(f"Error loading window geometry: {e}")
                self._center_window(default_width, default_height)
        else:
            # No config file - use default centered
            self._center_window(default_width, default_height)

    def _center_window(self, width: int, height: int):
        """Center window on screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _save_window_geometry(self):
        """Save current window position and size to config file."""
        try:
            # Get current geometry
            geometry = self.root.geometry()  # Format: "WIDTHxHEIGHT+X+Y"

            # Parse geometry string
            size, position = geometry.split('+', 1)
            width, height = map(int, size.split('x'))
            x, y = map(int, position.split('+'))

            # Save to config
            config = {
                'width': width,
                'height': height,
                'x': x,
                'y': y,
            }

            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)

        except Exception as e:
            print(f"Error saving window geometry: {e}")

    def _on_closing(self):
        """Handle window close event."""
        # Save window geometry
        self._save_window_geometry()

        # Stop any running task
        if self.is_running:
            self.is_running = False

        # Close window
        self.root.destroy()

    def run(self):
        """Run the UI."""
        # Check if onboarding is needed (after window is shown)
        self.root.after(500, lambda: check_and_run_onboarding(self.root))

        self.root.mainloop()


def main():
    """Main entry point."""
    monitor = CPAMonitor()
    monitor.run()


if __name__ == "__main__":
    main()

