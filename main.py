import tkinter as tk
from src.gui.menu_gui import Menu

if __name__ =="__main__":
    # Run Tkinter GUI
    root = tk.Tk()
    game = Menu(root)
    root.mainloop()
