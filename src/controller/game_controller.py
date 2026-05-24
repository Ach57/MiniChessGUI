from __future__ import annotations

from src.SearchAlgorithm.search import SearchAlgorithm
from src.Logger import MiniChessLogger
from typing import TYPE_CHECKING
import copy

if TYPE_CHECKING:
    from src.engine.game_engine import GameEngine
    from src.gui.chess_gui import BaseChessGUI

class GameController:
    """
    Base controller — shared logic for all game modes.

    Subclasses MUST implement:
        start() — wire callbacks and kick off the game loop
    """
    def __init__(self, engine: GameEngine, view: BaseChessGUI):
        self.engine = engine
        self.view = view
        self.logger = MiniChessLogger.get_instance()
    
    # ------------------------------------------------------------------ #
    #  Abstract hook                                                       #
    # ------------------------------------------------------------------ #
    
    def start(self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement start()"
        )
    
    # ------------------------------------------------------------------ #
    #  Shared logic — used by all subclasses                              #
    # ------------------------------------------------------------------ #
    def _apply_and_refresh(self, move: tuple) -> bool:
        """
        Apply a validated move, check for a winner, refresh the view.
        Returns True if the game is now over.
        """
        self.engine.apply_move(move)
        self.logger.info("Move applied: %s", move)

        winner = self.engine.is_game_over()
        if winner:
            self.view.update_board(winner)
            self.view.disable_buttons()
            self.logger.log_winner(winner)
            return True

        self.view.update_board(f"{self.engine.state['turn'].upper()} TURN")
        return False    

# ─────────────────────────────────────────────
#  Player vs Player
# ─────────────────────────────────────────────

class PvPController(GameController):
    
    def start(self) -> None:
        self.view.on_square_selected = self._handle_select
        self.view.on_move_attempted  = self._handle_move

    def _handle_select(self, x: int, y: int) -> None:
        piece = self.engine.state["board"][x][y]
        turn  = self.engine.state["turn"]

        if piece.startswith(turn[0]):
            self.view.highlight_square(x, y)
        elif piece != ".":
            self.view.show_error("You can't move your opponent's piece.")

    def _handle_move(self, origin: tuple, destination: tuple) -> None:
        if origin == destination:
            self.view.deselect_square(*origin)
            return

        move = (origin, destination)

        if not self.engine.is_valid_move(move):
            self.view.show_warning("Illegal move!")
            return

        self._apply_and_refresh(move)
        self.view.deselect_square(*origin)

# ─────────────────────────────────────────────
#  Player vs AI
# ─────────────────────────────────────────────

class PvAIController(GameController):

    def start(self) -> None:
        self.view.on_square_selected  = self._handle_select
        self.view.on_move_attempted   = self._handle_move
        self.view.on_ai_turn_requested = self._handle_ai_turn

    
    def _handle_select(self, x: int, y: int) -> None:
        piece = self.engine.state["board"][x][y]
        turn  = self.engine.state["turn"]

        if piece.startswith(turn[0]):
            self.view.highlight_square(x, y)
        elif piece != ".":
            self.view.show_error("You can't move your opponent's piece.")

    def _handle_move(self, origin: tuple, destination: tuple) -> None:
        if origin == destination:
            self.view.deselect_square(*origin)
            return

        move = (origin, destination)

        if not self.engine.is_valid_move(move):
            self.view.show_warning("Illegal move!")
            return

        game_over = self._apply_and_refresh(move)
        self.view.deselect_square(*origin)

        if not game_over:
            self.view.update_board("AI is thinking...")
            self.view.root.after(100, self._handle_ai_turn)

    def _handle_ai_turn(self) -> None:
        from src.SearchAlgorithm.search import SearchAlgorithm

        search = SearchAlgorithm(
            initial_state   = copy.deepcopy(self.engine.state),
            heuristic       = self.engine.heuristic_fn,
            valid_moves_fn  = self.engine.valid_moves_for_state,
            apply_move_fn   = self.engine.apply_move_to_state,
            is_game_over_fn = self.engine.is_game_over_for_state,
            alpha_beta      = self.engine.alpha_beta,
            max_time        = self.engine.max_time,
            maximizer       = self.engine.state["turn"] == "white",
        )

        score, best_move, time_spent = search.search_best_move(depth=3)
        self.logger.info("AI move: %s | score: %s | time: %.2fs", best_move, score, time_spent)

        if best_move is None:
            self.view.update_board("AI has no moves. Game over.")
            self.view.disable_buttons()
            return

        self.logger.log_move(
            player=self.engine.state["turn"],
            move=best_move,
            ai_time=time_spent,
            heuristic_score=score,
        )
        self._apply_and_refresh(best_move)

# ─────────────────────────────────────────────
#  AI vs AI
# ─────────────────────────────────────────────

class AiVsAiController(GameController):
    
    def start(self) -> None:
        # No human callbacks to wire — AI drives both sides
        self.view.root.after(100, self._handle_ai_turn)
        
    def _handle_ai_turn(self) -> None:
        from src.SearchAlgorithm.search import SearchAlgorithm

        search = SearchAlgorithm(
            initial_state   = copy.deepcopy(self.engine.state),
            heuristic       = self.engine.heuristic_fn,
            valid_moves_fn  = self.engine.valid_moves_for_state,
            apply_move_fn   = self.engine.apply_move_to_state,
            is_game_over_fn = self.engine.is_game_over_for_state,
            alpha_beta      = self.engine.alpha_beta,
            max_time        = self.engine.max_time,
            maximizer       = self.engine.state["turn"] == "white",
        )

        score, best_move, time_spent = search.search_best_move(depth=3)
        self.logger.info("AI move: %s | score: %s | time: %.2fs", best_move, score, time_spent)

        if best_move is None:
            self.view.update_board("No moves available. Game over.")
            self.view.disable_buttons()
            return

        self.logger.log_move(
            player=self.engine.state["turn"],
            move=best_move,
            ai_time=time_spent,
            heuristic_score=score,
        )
        game_over = self._apply_and_refresh(best_move)

        if not game_over:
            # Schedule the next AI move — keeps the UI responsive
            self.view.root.after(500, self._handle_ai_turn)


