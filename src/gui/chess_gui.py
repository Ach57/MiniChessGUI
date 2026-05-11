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

    """
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(GUIC.TITLE)
        self.selected_piece: tuple | None = None
        self.buttons = [
            [None for _ in range(GUIC.BOARD_SIZE)]
            for _ in range(GUIC.BOARD_SIZE)
        ]
        self._build_header()
        self.turnLabel = tk.Label(self.root, text="", font=GUIC.FONT_TURN)
        self.create_board()
        
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

    def __init__(
        self,
        root: tk.Tk,  
        max_turns: int  
    ):        
        self.engine = GameEngine(max_turns)    
        super().__init__(root)   # triggers create_board via base __init__

    # ------------------------------------------------------------------ #

    def _make_button_command(self, i: int, j: int):
        return lambda x=i, y=j: self.on_click(x, y)

    def on_click(self, x: int, y: int) -> None:
        """Handle piece selection and movement."""
        piece = self.engine.state["board"][x][y]

        if self.selected_piece is None:
            self._try_select(x, y, piece)
        else:
            self._try_move(x, y)

    # ------------------------------------------------------------------ #
    #  Private click helpers                                               #
    # ------------------------------------------------------------------ #

    def _try_select(self, x: int, y: int, piece: str) -> None:
        """Select a piece if it belongs to the current player."""
        if piece.startswith(self.engine.state["turn"][0]):
            self.selected_piece = (x, y)
            self.buttons[x][y].config(highlightbackground=GUIC.BTN_SELECTED_BG)
        elif piece != ".":
            messagebox.showerror("Error", "You can't move your opponent's piece.")
    
    def _try_move(self, x:int, y:int) -> None:
        """Attempt to move the selected piece to (x, y)."""
        old_x, old_y = self.selected_piece
        
        # Clicking the same square deselects the piece
        if (x,y) == (old_x, old_y):
            self.buttons[x][y].config(highlightbackground=GUIC.BTN_DEFAULT_BG)
            self.selected_piece = None
            return

        move = ((old_x, old_y), (x, y))

        if not self.engine.is_valid_move(move):      # ask the engine
            messagebox.showwarning("Warning", "Illegal move!")
            return

        self.engine.apply_move(move)                 # engine mutates state
        self.selected_piece = None

        winner = self.engine.is_game_over()          # engine checks win
        if winner:
            self.update_board(winner)
            self.disable_buttons()
        else:
            self.update_board(f"{self.engine.state['turn'].upper()} TURN")    


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
        """Human half-turn only — AI responds after."""
        if self.engine.state['turn'] != self.human_color:
            return # Ignore clicks when its AI turn
        
        piece = self.engine.state["board"][x][y]
        
        if self.selected_piece is None:
            self._try_select(x, y, piece)
        else:
            self._try_human_move(x, y)
    
    def _try_select(self, x: int, y: int, piece: str) -> None:
        if piece.startswith(self.engine.state["turn"][0]):
            self.selected_piece = (x, y)
            self.buttons[x][y].config(highlightbackground=GUIC.BTN_SELECTED_BG)
        elif piece != ".":
            messagebox.showerror("Error", "You can't move your opponent's piece.")

    def _try_human_move(self, x: int, y: int) -> None:
        old_x, old_y = self.selected_piece

        # Deselect on same square
        if (x, y) == (old_x, old_y):
            self.buttons[x][y].config(highlightbackground=GUIC.BTN_DEFAULT_BG)
            self.selected_piece = None
            return

        move = ((old_x, old_y), (x, y))

        if not self.engine.is_valid_move(move):
            messagebox.showwarning("Warning", "Illegal move!")
            return

        self.engine.apply_move(move)
        self.selected_piece = None

        winner = self.engine.is_game_over()
        if winner:
            self.update_board(winner)
            self.disable_buttons()
            return

        # Human move done — hand off to AI
        self.update_board(f"AI is thinking...")
        self.root.after(100, self.on_ai_turn_requested)  # 100ms lets the UI repaint
    
    def on_ai_turn_requested(self) -> None:
        """
        Callback slot — wired by the Controller after construction.
        Default is a no-op; Controller replaces it with the real handler.
        """
        pass

    
    def _trigger_ai_move(self) -> None:
        """Ask the search algorithm for a move and apply it."""
        # TODO: replace with real search call
        # ai_move = search.get_best_move(self.engine, self.engine.heuristic, self.engine.alpha_beta)
        # self.engine.apply_move(ai_move)

        winner = self.engine.is_game_over()
        if winner:
            self.update_board(winner)
            self.disable_buttons()
        else:
            self.update_board(f"{self.engine.state['turn'].upper()} TURN")
