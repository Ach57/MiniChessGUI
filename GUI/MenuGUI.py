import tkinter as tk
from tkinter import ttk
from .ChessGUI import *
from Logger.MiniChessLogger import Logger

custom_logger = Logger().get_logger()

class Menu:
    def __init__(self, root: tk.Tk):
        
        self.root = root
        self.root.title("Mini Chess Game")

        self.headerlabel = tk.Label(root, text="Welcome to Mini Chess Game", font=('Arial', 24))
        self.headerlabel.grid(row=0, column=0, columnspan=2, pady=20)

        # Game mode selection
        self.mode_label = tk.Label(root, text="Choose game mode:", font=('Arial', 14))
        self.mode_label.grid(row=1, column=0, sticky="e")

        self.mode_var = tk.StringVar()
        self.mode_var.set("Select a mode...")
        self.mode_options = ["Player vs Player", "Player vs AI", "AI vs Player", "AI vs AI", "Exit"]
        self.mode_dropdown = ttk.Combobox(root, textvariable=self.mode_var, values=self.mode_options, state="readonly")
        self.mode_dropdown.grid(row=1, column=1, padx=10)
        self.mode_dropdown.bind("<<ComboboxSelected>>", self.show_ai_options)

        # Max time
        self.max_time_label = tk.Label(root, text="Max Time (sec):", font=('Arial', 12))
        self.max_time_entry = tk.Entry(root)

        # Max turns
        self.max_turns_label = tk.Label(root, text="Max Turns:", font=('Arial', 12))
        self.max_turns_entry = tk.Entry(root)

        # Heuristic
        self.heuristic_label = tk.Label(root, text="Heuristic (e0, e1, e2):", font=('Arial', 12))
        self.heuristic_var = tk.StringVar()
        self.heuristic_var.set("Select a Heuristic ...")
        self.heuristic_dropdown = ttk.Combobox(root, textvariable=self.heuristic_var, values=["e0", "e1", "e2"], state="readonly")

        # Alpha-beta
        self.alpha_beta_var = tk.BooleanVar()
        self.alpha_beta_check = tk.Checkbutton(root, text="Enable Alpha-Beta Pruning", variable=self.alpha_beta_var, font=('Arial', 12))

        # Start button
        self.start_button = tk.Button(root, text="Start Game", font=('Arial', 14), command=self.start_game)
        self.start_button.grid(row=10, column=0, columnspan=2, pady=20)            
                
    def show_ai_options(self, event=None):
        mode = self.mode_var.get()
        # Clear old options
        for widget in [self.max_time_label, self.max_time_entry,
                       self.max_turns_label, self.max_turns_entry,
                       self.heuristic_label, self.heuristic_dropdown,
                       self.alpha_beta_check]:
            widget.grid_remove()
            
        if "AI" in mode:
            self.max_time_label.grid(row=2, column=0, sticky="e")
            self.max_time_entry.grid(row=2, column=1, pady=5)
            
            self.max_turns_label.grid(row=3, column=0, sticky="e")
            self.max_turns_entry.grid(row=3, column=1, pady=5)

            self.heuristic_label.grid(row=4, column=0, sticky="e")
            self.heuristic_dropdown.grid(row=4, column=1, pady=5)

            self.alpha_beta_check.grid(row=5, column=0, columnspan=2, pady=5)

        elif mode == "Player vs Player":
            self.max_turns_label.grid(row=3, column=0, sticky="e")
            self.max_turns_entry.grid(row=3, column=1, pady=5)
            
    def start_game(self):
        mode = self.mode_var.get() 
        if mode =="Exit":
            custom_logger.info("Game Existed")
            self.root.quit()
        else:
            max_turn = self.max_turns_entry.get()
            custom_logger.info(f"max_turn set = {max_turn}")
            
            if mode == "Player vs Player": # Start player vs player
                self.root.destroy()
                root = tk.Tk()
                game = ChessGUI(root, player1="Player", player2="Player")
                root.mainloop()
            if "AI" in mode:
                max_time = self.max_time_entry.get()
                heuristic = self.heuristic_var.get()
                alpha_beta = self.alpha_beta_var.get()
                custom_logger.info(f"max_time: {max_time}, heuristic: {heuristic}, alpha_beta: {alpha_beta}")
                if mode =="Player vs AI":
                    self.root.destroy()
                    root = tk.Tk()
                    game = playerVsAi(root)
                    root.mainloop()
                