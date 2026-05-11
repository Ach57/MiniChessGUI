from __future__ import annotations

from src.SearchAlgorithm.search import SearchAlgorithm
from src.Logger.mini_chess_logger import Logger
from typing import TYPE_CHECKING
import copy

if TYPE_CHECKING:
    from src.engine.game_engine import GameEngine
    from src.gui.chess_gui import PlayerVsAiGui

logger = Logger().get_logger()

class GameController:
    def __init__(self, engine: GameEngine, view: PlayerVsAiGui):
        self.engine = engine
        self.view = view
        
        # Wire the view's callback slot to the controller's handler
        self.view.on_ai_turn_requested = self._handle_ai_turn
    
    def _handle_ai_turn(self):
        """Run the search, apply the best move, refresh the view."""
        search = SearchAlgorithm(
            initial_state   = copy.deepcopy(self.engine.state),
            heuristic       = self.engine.heuristic_fn,
            valid_moves_fn  = self.engine.valid_moves,
            apply_move_fn   = self.engine.apply_move,
            is_game_over_fn = self.engine.is_game_over,
            alpha_beta      = self.engine.alpha_beta,
            max_time        = self.engine.max_time,
            maximizer       = self.engine.state["turn"] == "white",
        )
        score, best_move, time_spent = search.search_best_move(depth=3)
        logger.info("AI move: %s | score: %s | time: %.2fs", best_move, score, time_spent)
        
        if best_move is None:
            # No moves available — game is effectively over
            self.view.update_board("AI has no moves. Game over.")
            self.view.disable_buttons()
            return

        self.engine.apply_move(best_move)

        winner = self.engine.is_game_over()
        if winner:
            self.view.update_board(winner)
            self.view.disable_buttons()
        else:
            self.view.update_board(f"{self.engine.state['turn'].upper()} TURN")


        