from __future__ import annotations

import tkinter as tk
from src.gui.menu_gui import Menu

def run() -> None:    
    """
        Application entry point.
    """
    # Run Tkinter GUI    
    app = Menu(root = tk.Tk())
    app.runGame()