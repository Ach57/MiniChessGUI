from __future__ import annotations

'''-------------  GUI Libraries ----------------'''
import tkinter as tk
from tkinter import messagebox

'''-------------  Pieces Configuration ----------------'''
from src.constants.game import GameConstants as GC
from src.constants.gui import GUIConstants as GUIC
from src.engine.game_engine import GameEngine

# ─────────────────────────────────────────────
#  Base class — shared structure & logic
# ─────────────────────────────────────────────
class BaseChessGUI:
    """
    Shared foundation for all Chess GUI modes.

    Subclasses MUST implement:
        _make_button_command(i, j) -> callable | None
    
    Subclasses MUST set self.engine before calling super().__init__().

    Callback slots (wired by the Controller via start()):
        on_square_selected(x, y)          — a square was clicked with no piece selected
        on_move_attempted(origin, dest)   — a destination square was clicked after selection
        on_ai_turn_requested()            — human half-turn is complete; AI should move
    """
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(GUIC.TITLE)
        self.selected_piece: tuple | None = None
        self.buttons = [
            [None for _ in range(GUIC.BOARD_SIZE)]
            for _ in range(GUIC.BOARD_SIZE)
        ]
        # Callback slots — Controller wires these in start()
        self.on_square_selected = None
        self.on_move_attempted  = None
        self.on_ai_turn_requested = None
        self._build_header()
        self.turnLabel = tk.Label(self.root, text="", font=GUIC.FONT_TURN)
        self.create_board()
        
    # ------------------------------------------------------------------ #
    #  UI runner                                                         #
    # ------------------------------------------------------------------ #    
    
    def runChessGame(self) -> None:
        self.root.mainloop()
        
    # ------------------------------------------------------------------ #
    #  UI builders                                                         #
    # ------------------------------------------------------------------ #
    
    def _build_header(self) -> None:
        tk.Label(
            master=self.root, text=GUIC.HEADER_TEXT, font= GUIC.FONT_HEADER
        ).grid(row=0, columnspan=GUIC.BOARD_SIZE)

    def create_board(self) -> None:
        """Build the button grid. Delegates button command to subclass."""
        for i in range(GUIC.BOARD_SIZE):
            for j in range(GUIC.BOARD_SIZE):
                piece = self.engine.state["board"][i][j]
                cmd = self._make_button_command(i, j)   # hook for subclasses
                btn = tk.Button(
                    self.root,
                    text=GC.PIECES[piece],
                    font=GUIC.FONT_HEADER,
                    highlightbackground=GUIC.BTN_DEFAULT_BG,
                    width=GUIC.BTN_WIDTH,
                    height=GUIC.BTN_HEIGHT,
                    command=cmd,
                )
                btn.grid(row=i + 1, column=j)
                self.buttons[i][j] = btn

        self.turnLabel.config(text=f"{self.engine.state['turn'].upper()} TURN")
        self.turnLabel.grid(row=GUIC.BOARD_SIZE + 1, columnspan=GUIC.BOARD_SIZE)
    
    def update_board(self, message: str) -> None:
        """Refresh every button's text and reset highlight colours."""
        for i in range(GUIC.BOARD_SIZE):
            for j in range(GUIC.BOARD_SIZE):
                piece = self.engine.state["board"][i][j]
                self.buttons[i][j].config(
                    text=GC.PIECES[piece],
                    highlightbackground=GUIC.BTN_DEFAULT_BG,
                )
        self.turnLabel.config(text=message)

    def disable_buttons(self) -> None:
        """Lock the board at end-of-game."""
        for row in self.buttons:
            for btn in row:
                btn.config(state=tk.DISABLED)

    # ------------------------------------------------------------------ #
    #  UI actions — called BY the Controller, never self-triggered         #
    # ------------------------------------------------------------------ #

    def highlight_square(self, x: int, y: int) -> None:
        self.selected_piece = (x, y)
        self.buttons[x][y].config(highlightbackground=GUIC.BTN_SELECTED_BG)

    def deselect_square(self, x: int, y: int) -> None:
        self.selected_piece = None
        self.buttons[x][y].config(highlightbackground=GUIC.BTN_DEFAULT_BG)

    def show_error(self, message: str) -> None:
        messagebox.showerror("Error", message)

    def show_warning(self, message: str) -> None:
        messagebox.showwarning("Warning", message)

    # ------------------------------------------------------------------ #
    #  Abstract hook — subclasses MUST override                            #
    # ------------------------------------------------------------------ #
    def _make_button_command(self, i: int, j: int):
        """
        Return the callable to bind to button (i, j), or None for no command.
        Subclasses override this to inject click behaviour without
        duplicating create_board().
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _make_button_command()"
        )

# ─────────────────────────────────────────────
#  Player vs Player
# ─────────────────────────────────────────────

class PlayerVsPlayerGui(BaseChessGUI):
    """Human vs Human mode."""

    def __init__(self, root: tk.Tk, engine: GameEngine):
        self.engine = engine
        super().__init__(root)
    # ------------------------------------------------------------------ #

    def _make_button_command(self, i: int, j: int):
        return lambda x=i, y=j: self.on_click(x, y)

    def on_click(self, x: int, y: int) -> None:
        """Forward click to the appropriate controller callback."""
        if self.selected_piece is None:
            if self.on_square_selected:
                self.on_square_selected(x, y)
        else:
            if self.on_move_attempted:
                self.on_move_attempted(self.selected_piece, (x, y))


# ─────────────────────────────────────────────
#  Player vs AI
# ─────────────────────────────────────────────

class PlayerVsAiGui(BaseChessGUI):
    """Human vs AI mode — AI logic to be wired in."""

    def __init__(self,
                root: tk.Tk,
                engine: GameEngine,
                human_color: str = "white" # determines who moves first
    ):
        self.human_color = human_color        
        self.engine = engine
        super().__init__(root)

    def _make_button_command(self, i: int, j: int):
        return lambda x=i, y=j: self.on_click(x, y)

    def on_click(self, x: int, y: int) -> None:
        """Forward human clicks to controller callbacks; ignore clicks during AI's turn."""
        if self.engine.state['turn'] != self.human_color:
            return  # Ignore clicks when it's AI's turn
        if self.selected_piece is None:
            if self.on_square_selected:
                self.on_square_selected(x, y)
        else:
            if self.on_move_attempted:
                self.on_move_attempted(self.selected_piece, (x, y))


# ─────────────────────────────────────────────
#  AI vs AI
# ─────────────────────────────────────────────

class AiVsAiGui(BaseChessGUI):
    """AI vs AI mode — board display only, no human interaction."""

    def __init__(self, root: tk.Tk, engine: GameEngine):
        self.engine = engine
        super().__init__(root)

    def _make_button_command(self, i: int, j: int):
        return None  # No human interaction
