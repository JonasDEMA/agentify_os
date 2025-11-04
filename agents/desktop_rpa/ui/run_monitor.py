"""Run the CPA Monitor UI."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.desktop_rpa.ui.cpa_monitor import CPAMonitor


def main():
    """Main entry point."""
    print("🚀 Starting CPA Agent Monitor...")
    monitor = CPAMonitor()
    monitor.run()


if __name__ == "__main__":
    main()

