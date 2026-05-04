import tkinter as tk
from src.gui.menu_gui import Menu

def run() -> None:    
    """
        Application entry point.
    """
    # Run Tkinter GUI
    root = tk.Tk()
    game = Menu(root)
    root.mainloop()