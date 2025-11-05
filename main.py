"""
Instagram Link Organizer
Main application entry point
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(__file__))

from src.gui.main_window import main

if __name__ == "__main__":
    main()
