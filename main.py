"""
Valorant Caster Companion — entry point.
Run with:  python main.py
"""
import sys
from pathlib import Path

# Make sure imports resolve from this directory
sys.path.insert(0, str(Path(__file__).parent))

from ui.app import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()