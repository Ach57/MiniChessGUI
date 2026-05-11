from __future__ import annotations

import copy
import time
from collections import defaultdict
from typing import Callable

from src.heuristics.heuristics import get_pieces_count


# ─────────────────────────────────────────────
#  Custom exception — replaces exit() calls
# ─────────────────────────────────────────────

class SearchTimeout(Exception):
    """Raised when the search exceeds its time budget.
    
    Caught by search_best_move(), which returns the best
    move found so far rather than crashing the process.
    """


# ─────────────────────────────────────────────
#  Search Algorithm
# ─────────────────────────────────────────────

class SearchAlgorithm:
    """
    Minimax search with optional Alpha-Beta pruning.

    Design contract
    ---------------
    - Receives a **snapshot** of the engine state (a plain dict).
      It never holds a reference to the live GameEngine, the GUI,
      or the logger — those are Controller concerns.
    - On timeout it raises SearchTimeout internally, catches it in
      search_best_move(), and returns the best move found so far.
      It never calls exit().
    - Deep copies only the state dict (not a whole game object) when
      branching the search tree.
    - Minimax and Alpha-Beta share one recursive method (_minimax);
      pruning is toggled by self.alpha_beta.
    """

    def __init__(
        self,
        initial_state: dict,
        heuristic: Callable,
        valid_moves_fn: Callable,
        apply_move_fn: Callable,
        is_game_over_fn: Callable,
        alpha_beta: bool = True,
        max_time: float = 5.0,
        maximizer: bool = True,
    ) -> None:
        """
        Args:
            initial_state:    Deep-copied state dict from the engine.
            heuristic:        Callable(pieces_count, game_state) -> int.
            valid_moves_fn:   Callable(game_state) -> list[tuple].
            apply_move_fn:    Callable(game_state, move) -> new_game_state dict.
            is_game_over_fn:  Callable(game_state) -> str | None.
            alpha_beta:       True → Alpha-Beta pruning; False → plain Minimax.
            max_time:         Time budget in seconds.
            maximizer:        True if the AI plays as the maximizing side (white).
        """
        self.initial_state   = initial_state
        self.heuristic       = heuristic
        self.valid_moves_fn  = valid_moves_fn
        self.apply_move_fn   = apply_move_fn
        self.is_game_over_fn = is_game_over_fn
        self.alpha_beta      = alpha_beta
        self.max_time        = max_time
        self.maximizer       = maximizer

        # Diagnostics — reset each call to search_best_move()
        self.cumulative_states: int = 0
        self.states_by_depth: defaultdict[int, int] = defaultdict(int)
        self.start_time: float = 0.0

    # ------------------------------------------------------------------ #
    #  Public entry point                                                  #
    # ------------------------------------------------------------------ #

    def search_best_move(self, depth: int) -> tuple[int, tuple | None, float]:
        """
        Run the search and return the best move found within the time budget.

        Returns:
            (best_score, best_move, time_spent)
            best_move is None only if no moves are available (game already over).
        """
        # Reset diagnostics for this search call
        self.cumulative_states = 0
        self.states_by_depth.clear()
        self.start_time = time.time()

        best_score, best_move = 0, None

        try:
            best_score, best_move = self._minimax(
                state=self.initial_state,
                depth=depth,
                alpha=float("-inf"),
                beta=float("+inf"),
                maximizing=self.maximizer,
            )
        except SearchTimeout:
            # Return the best move found before the clock ran out.
            # The controller decides how to handle a timeout (log, warn, etc.)
            pass

        time_spent = time.time() - self.start_time
        return best_score, best_move, time_spent

    # ------------------------------------------------------------------ #
    #  Core recursive search (Minimax + optional Alpha-Beta)              #
    # ------------------------------------------------------------------ #

    def _minimax(
        self,
        state: dict,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
    ) -> tuple[int, tuple | None]:
        """
        Single recursive method for both Minimax and Alpha-Beta.
        Pruning only activates when self.alpha_beta is True.

        Args:
            state:      Current board state dict (already a copy).
            depth:      Remaining search depth.
            alpha:      Best score the maximizer can guarantee so far.
            beta:       Best score the minimizer can guarantee so far.
            maximizing: True → maximizing player's turn.

        Returns:
            (best_score, best_move)
        """
        self._check_timeout()

        # Base case: leaf node or terminal state
        if depth == 0 or self.is_game_over_fn() is not None:
            self.cumulative_states += 1
            return self._evaluate(state), None

        moves = self.valid_moves_fn()
        if not moves:
            # No moves available — evaluate as terminal
            self.cumulative_states += 1
            return self._evaluate(state), None

        best_move = None

        if maximizing:
            best_score = float("-inf")
            for move in moves:
                child_state = self._branch(state, move, depth)
                score, _ = self._minimax(child_state, depth - 1, alpha, beta, False)

                if score > best_score:
                    best_score = score
                    best_move  = move

                alpha = max(alpha, score)
                if self.alpha_beta and beta <= alpha:
                    break  # β-cutoff

            return best_score, best_move

        else:  # minimizing
            best_score = float("+inf")
            for move in moves:
                child_state = self._branch(state, move, depth)
                score, _ = self._minimax(child_state, depth - 1, alpha, beta, True)

                if score < best_score:
                    best_score = score
                    best_move  = move

                beta = min(beta, score)
                if self.alpha_beta and beta <= alpha:
                    break  # α-cutoff

            return best_score, best_move

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _check_timeout(self) -> None:
        """Raise SearchTimeout if the time budget is exhausted."""
        if time.time() - self.start_time >= self.max_time:
            raise SearchTimeout()

    def _branch(self, state: dict, move: tuple, depth: int) -> dict:
        """
        Copy only the state dict and apply the move to the copy.
        Counts the new node for diagnostics.
        """
        new_state = copy.deepcopy(state)       # dict only — not a whole game object
        self.apply_move_fn(move)
        self.states_by_depth[depth] += 1
        return new_state

    def _evaluate(self, state: dict) -> int:
        """Score a leaf node using the chosen heuristic."""
        pieces_count = get_pieces_count(state)
        return self.heuristic(pieces_count, state)

    # ------------------------------------------------------------------ #
    #  Diagnostics                                                         #
    # ------------------------------------------------------------------ #

    def get_stats(self) -> dict:
        """Return search diagnostics after the last search_best_move() call."""
        return {
            "cumulative_states": self.cumulative_states,
            "states_by_depth":   dict(self.states_by_depth),
            "alpha_beta":        self.alpha_beta,
            "max_time":          self.max_time,
        }