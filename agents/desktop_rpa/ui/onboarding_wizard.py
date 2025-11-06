"""OnBoarding Wizard for CPA Agent - First-time setup."""

import tkinter as tk
from tkinter import messagebox, ttk

from agents.desktop_rpa.config.settings import settings


class OnBoardingWizard:
    """OnBoarding wizard for first-time setup."""

    def __init__(self, parent=None):
        """Initialize the wizard.
        
        Args:
            parent: Parent window (optional)
        """
        self.parent = parent
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent) if parent else tk.Tk()
        self.dialog.title("🚀 Welcome to CPA Agent")
        self.dialog.geometry("600x600")
        self.dialog.resizable(True, True)
        self.dialog.minsize(600, 600)
        
        # Center window
        self._center_window()
        
        # Make modal
        if parent:
            self.dialog.transient(parent)
            self.dialog.grab_set()
        
        # Setup UI
        self._setup_ui()
        
    def _center_window(self):
        """Center the window on screen."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def _setup_ui(self):
        """Setup the UI."""
        # Main frame with grid layout
        main_frame = ttk.Frame(self.dialog, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        row = 0

        # Welcome header
        welcome_label = ttk.Label(
            main_frame,
            text="🤖 Welcome to CPA Agent!",
            font=("Segoe UI", 16, "bold")
        )
        welcome_label.grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1

        subtitle_label = ttk.Label(
            main_frame,
            text="Let's get you set up in just a few seconds",
            font=("Segoe UI", 10)
        )
        subtitle_label.grid(row=row, column=0, sticky=tk.W, pady=(0, 20))
        row += 1

        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, sticky=(tk.E, tk.W), pady=(0, 20))
        row += 1

        # Phone number section
        phone_frame = ttk.LabelFrame(main_frame, text="📱 SMS Notifications", padding="20")
        phone_frame.grid(row=row, column=0, sticky=(tk.E, tk.W), pady=(0, 20))
        phone_frame.columnconfigure(0, weight=1)
        row += 1

        info_label = ttk.Label(
            phone_frame,
            text="The CPA Agent can send you SMS notifications when it needs your input.\n"
                 "Please enter your phone number:",
            wraplength=450,
            justify=tk.LEFT,
            font=("Segoe UI", 10)
        )
        info_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

        # Phone number label
        ttk.Label(phone_frame, text="Phone Number:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))

        # Phone number input
        self.phone_var = tk.StringVar(value="+49")
        self.phone_entry = ttk.Entry(phone_frame, textvariable=self.phone_var, font=("Segoe UI", 11))
        self.phone_entry.grid(row=2, column=0, sticky=(tk.E, tk.W), ipady=5, pady=(0, 15))
        self.phone_entry.focus()

        # Format hint
        hint_label = ttk.Label(
            phone_frame,
            text="Format: +49... (include country code)",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        hint_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 2))

        # Example
        example_label = ttk.Label(
            phone_frame,
            text="Example: +4915143233730",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        example_label.grid(row=4, column=0, sticky=tk.W)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, sticky=(tk.E, tk.W), pady=(20, 0))
        button_frame.columnconfigure(1, weight=1)  # Space between buttons
        row += 1

        # Skip button (left)
        skip_btn = ttk.Button(
            button_frame,
            text="⏭️ Skip for now",
            command=self._skip,
            width=15
        )
        skip_btn.grid(row=0, column=0, sticky=tk.W)

        # Continue button (right) - larger and more prominent
        continue_btn = tk.Button(
            button_frame,
            text="✅ Continue",
            command=self._continue,
            bg="#0078D4",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        continue_btn.grid(row=0, column=2, sticky=tk.E)

        # Hover effect for continue button
        def on_enter(e):
            continue_btn.config(bg="#005A9E")

        def on_leave(e):
            continue_btn.config(bg="#0078D4")

        continue_btn.bind("<Enter>", on_enter)
        continue_btn.bind("<Leave>", on_leave)

        # Bind Enter key
        self.phone_entry.bind('<Return>', lambda e: self._continue())
        
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation
        if not phone:
            return False
        
        # Must start with +
        if not phone.startswith('+'):
            return False
        
        # Must have at least 10 digits after +
        digits = ''.join(c for c in phone[1:] if c.isdigit())
        if len(digits) < 10:
            return False
        
        return True
    
    def _continue(self):
        """Continue with phone number."""
        phone = self.phone_var.get().strip()
        
        if not self._validate_phone(phone):
            messagebox.showerror(
                "Invalid Phone Number",
                "Please enter a valid phone number with country code.\n\n"
                "Format: +49... (at least 10 digits)\n"
                "Example: +4915143233730",
                parent=self.dialog
            )
            self.phone_entry.focus()
            return
        
        # Save to settings
        self.result = phone
        self.dialog.destroy()
    
    def _skip(self):
        """Skip phone number setup."""
        result = messagebox.askyesno(
            "Skip Setup",
            "Are you sure you want to skip SMS notifications?\n\n"
            "You can always add your phone number later in the settings.",
            parent=self.dialog
        )
        
        if result:
            self.result = None
            self.dialog.destroy()
    
    def show(self) -> str | None:
        """Show the wizard and return the phone number.
        
        Returns:
            Phone number if entered, None if skipped
        """
        self.dialog.wait_window()
        return self.result


def check_and_run_onboarding(parent=None) -> bool:
    """Check if onboarding is needed and run it.
    
    Args:
        parent: Parent window (optional)
        
    Returns:
        True if onboarding was completed, False if skipped or already done
    """
    # Check if phone number is already set
    if settings.user_phone_number:
        return False
    
    # Run onboarding
    wizard = OnBoardingWizard(parent)
    phone = wizard.show()
    
    if phone:
        # Save to .env file
        env_file = ".env"
        try:
            # Read existing .env
            lines = []
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except FileNotFoundError:
                pass
            
            # Update or add phone number
            found = False
            for i, line in enumerate(lines):
                if line.startswith('USER_PHONE_NUMBER='):
                    lines[i] = f'USER_PHONE_NUMBER={phone}\n'
                    found = True
                    break
            
            if not found:
                lines.append(f'USER_PHONE_NUMBER={phone}\n')
            
            # Write back
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            # Update settings
            settings.user_phone_number = phone
            
            return True
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to save phone number: {e}",
                parent=parent
            )
            return False
    
    return False


if __name__ == "__main__":
    # Test the wizard
    wizard = OnBoardingWizard()
    phone = wizard.show()
    print(f"Phone number: {phone}")

