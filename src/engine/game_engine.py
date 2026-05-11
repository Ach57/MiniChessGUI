# src/engine/game_engine.py
from typing import Callable
from src.pieces import *
from src.constants.game import GameConstants as GC
from src.constants.gui import GUIConstants as GUIC

BOARD_SIZE = GUIC.BOARD_SIZE

MOVEMENT_RULES = {
    "K": king_moves,
    "Q": queen_moves,
    "B": bishop_moves,
    "N": knight_moves,
    "p": pawn_moves,
}

class GameEngine:
    """
    Owns all game logic: state, rules, and state mutation.
    Completely independent of any GUI framework.
    """

    def __init__(self,
                 max_turns: int = 100,
                max_time: float | None = None,
                heuristic_fn: Callable | None = None,
                alpha_beta: bool | None = None,):
        
        self.max_turns = max_turns
        self.max_time = max_time
        self.heuristic_fn = heuristic_fn
        self.alpha_beta = alpha_beta
        
        self.state = self._fresh_state()

    def _fresh_state(self) -> dict:
        """Return a clean starting game state (deep-copied from constants)."""
        import copy
        state = copy.deepcopy(GC.state)   # never mutate the constant directly 
        state['turn_count'] = 0
        return state
        

    # ------------------------------------------------------------------ #
    #  Queries  (read-only — never mutate self.state)                     #
    # ------------------------------------------------------------------ #

    def valid_moves(self) -> list[tuple]:
        """All legal moves for the side whose turn it is."""
        board = self.state["board"]
        turn  = self.state["turn"]
        moves = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = board[row][col]
                if piece == "." :
                    continue

                piece_color = "white" if piece[0] == "w" else "black"
                if piece_color != turn:
                    continue

                move_fn = MOVEMENT_RULES.get(piece[1], lambda pos, state: [])
                for end_row, end_col in move_fn((row, col), self.state):
                    if 0 <= end_row < BOARD_SIZE and 0 <= end_col < BOARD_SIZE:
                        moves.append(((row, col), (end_row, end_col)))

        return moves

    def is_valid_move(self, move: tuple) -> bool:
        """Check whether a specific move is legal."""
        current_pos, destination = move
        board = self.state["board"]

        try:
            player = board[current_pos[0]][current_pos[1]]
        except IndexError:
            return False

        if player == ".":
            return False

        turn = self.state["turn"]
        if (player[0] == "w" and turn != "white") or \
           (player[0] == "b" and turn != "black"):
            return False

        return (current_pos, destination) in self.valid_moves()

    def is_game_over(self) -> str | None:
        """
        Returns the winner string if the game is over, None otherwise.
        Checked AFTER apply_move(), before the next turn.
        """
        board = self.state["board"]
        pieces_on_board = [p for row in board for p in row if p != "."]

        if "wK" not in pieces_on_board:
            return "Black wins! White's King is captured."
        if "bK" not in pieces_on_board:
            return "White wins! Black's King is captured."
        if self.state['turn_count'] >= self.max_turns:
            return f"Draw — maximum turns ({self.max_turns}) reached."
        return None

    # ------------------------------------------------------------------ #
    #  Commands  (mutate self.state)                                       #
    # ------------------------------------------------------------------ #

    def apply_move(self, move: tuple) -> None:
        """
        Commit a move to the board. Caller must have validated it first.
        Handles pawn promotion and turn switching.
        """
        (old_x, old_y), (x, y) = move
        piece = self.state["board"][old_x][old_y]

        self.state["board"][x][y]         = piece
        self.state["board"][old_x][old_y] = "."

        if piece in ("wp", "bp"):
            self._promote_pawn((x, y))

        self.state['turn_count'] +=1
        self.state["turn"] = "white" if self.state["turn"] == "black" else "black"

    def _promote_pawn(self, position: tuple) -> None:
        """Promote a pawn that has reached the far rank."""
        promote_pawn(position, game_state=self.state)   # delegates to pieces module