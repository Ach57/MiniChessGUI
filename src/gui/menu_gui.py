import tkinter as tk
from tkinter import ttk

from .chess_gui import PlayerVsPlayerGui, PlayerVsAi
from src.Logger.mini_chess_logger import Logger
from src.constants.menu import MenuConstants as MC

logger = Logger().get_logger()


class Menu:
    """Main menu window for Mini Chess Game."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(MC.TITLE)

        self._build_header()
        self._build_mode_selector()
        self._build_ai_options()   # creates widgets but hides them
        self._build_start_button()

    # ------------------------------------------------------------------ #
    #  Private builders — called once from __init__                        #
    # ------------------------------------------------------------------ #

    def _build_header(self) -> None:
        tk.Label(
            self.root, text=MC.HEADER_TEXT, font=MC.FONT_HEADER
        ).grid(row=0, column=0, columnspan=2, pady=20)

    def _build_mode_selector(self) -> None:
        tk.Label(
            self.root, text="Choose game mode:", font=MC.FONT_LABEL
        ).grid(row=1, column=0, sticky="e")

        self.mode_var = tk.StringVar(value=MC.DEFAULT_MODE_PLACEHOLDER)
        self.mode_dropdown = ttk.Combobox(
            self.root,
            textvariable=self.mode_var,
            values=MC.GAME_MODES,
            state="readonly",
        )
        self.mode_dropdown.grid(row=1, column=1, padx=10)
        self.mode_dropdown.bind("<<ComboboxSelected>>", self._on_mode_selected)

    def _build_ai_options(self) -> None:
        """Create all optional widgets; they are shown/hidden by _on_mode_selected."""
        root = self.root

        self.max_time_label = tk.Label(root, text="Max Time (sec):", font=MC.FONT_SMALL)
        self.max_time_entry = tk.Entry(root)

        self.max_turns_label = tk.Label(root, text="Max Turns:", font=MC.FONT_SMALL)
        self.max_turns_entry = tk.Entry(root)

        self.heuristic_label = tk.Label(root, text="Heuristic (e0, e1, e2):", font=MC.FONT_SMALL)
        self.heuristic_var = tk.StringVar(value=MC.DEFAULT_HEURISTIC_PLACEHOLDER)
        self.heuristic_dropdown = ttk.Combobox(
            root,
            textvariable=self.heuristic_var,
            values=MC.HEURISTICS,
            state="readonly",
        )

        self.alpha_beta_var = tk.BooleanVar()
        self.alpha_beta_check = tk.Checkbutton(
            root,
            text="Enable Alpha-Beta Pruning",
            variable=self.alpha_beta_var,
            font=MC.FONT_SMALL,
        )

        self._all_ai_widgets = [
            self.max_time_label, self.max_time_entry,
            self.max_turns_label, self.max_turns_entry,
            self.heuristic_label, self.heuristic_dropdown,
            self.alpha_beta_check,
        ]

    def _build_start_button(self) -> None:
        tk.Button(
            self.root,
            text="Start Game",
            font=MC.FONT_BUTTON,
            command=self._start_game,
        ).grid(row=10, column=0, columnspan=2, pady=20)

    # ------------------------------------------------------------------ #
    #  Event handlers                                                      #
    # ------------------------------------------------------------------ #

    def _on_mode_selected(self, event=None) -> None:
        """Show or hide optional fields depending on the selected game mode."""
        self._hide_all_ai_widgets()
        mode = self.mode_var.get()

        if "AI" in mode:
            self._show_ai_widgets()
        elif mode == "Player vs Player":
            self._show_pvp_widgets()

    # ------------------------------------------------------------------ #
    #  Widget visibility helpers                                           #
    # ------------------------------------------------------------------ #

    def _hide_all_ai_widgets(self) -> None:
        for widget in self._all_ai_widgets:
            widget.grid_remove()

    def _show_ai_widgets(self) -> None:
        self.max_time_label.grid(row=2, column=0, sticky="e")
        self.max_time_entry.grid(row=2, column=1, pady=5)

        self.max_turns_label.grid(row=3, column=0, sticky="e")
        self.max_turns_entry.grid(row=3, column=1, pady=5)

        self.heuristic_label.grid(row=4, column=0, sticky="e")
        self.heuristic_dropdown.grid(row=4, column=1, pady=5)

        self.alpha_beta_check.grid(row=5, column=0, columnspan=2, pady=5)

    def _show_pvp_widgets(self) -> None:
        self.max_turns_label.grid(row=3, column=0, sticky="e")
        self.max_turns_entry.grid(row=3, column=1, pady=5)

    # ------------------------------------------------------------------ #
    #  Game launching                                                      #
    # ------------------------------------------------------------------ #

    def _start_game(self) -> None:
        mode = self.mode_var.get()

        if mode == "Exit":
            logger.info("Game exited from menu")
            self.root.quit()
            return

        max_turns = self.max_turns_entry.get()
        logger.info("max_turns set = %s", max_turns)

        if mode == "Player vs Player":
            self._launch_pvp()
        elif "AI" in mode:
            self._launch_ai_mode(mode)

    def _launch_pvp(self) -> None:
        self.root.destroy()
        root = tk.Tk()
        PlayerVsPlayerGui(root, player1="Player", player2="Player")
        root.mainloop()

    def _launch_ai_mode(self, mode: str) -> None:
        max_time  = self.max_time_entry.get()
        heuristic = self.heuristic_var.get()
        alpha_beta = self.alpha_beta_var.get()
        logger.info("max_time=%s | heuristic=%s | alpha_beta=%s", max_time, heuristic, alpha_beta)

        self.root.destroy()
        root = tk.Tk()

        if mode == "Player vs AI":
            PlayerVsAi(root)
        # TODO: handle "AI vs Player" and "AI vs AI" here

        root.mainloop()