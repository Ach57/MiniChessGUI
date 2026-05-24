"""
Unit tests for GameEngine — state queries and mutations.
All tests operate on engine.state or explicit state dicts; no GUI involved.
"""
import copy
import pytest
from tests.unit.conftest import empty_board, make_state

from src.engine.game_engine import GameEngine


# ── factory helpers ────────────────────────────────────────────────────────────

def engine_from_board(board, turn="white", turn_count=0, max_turns=100) -> GameEngine:
    """Build a GameEngine and replace its state with the supplied board."""
    eng = GameEngine(max_turns=max_turns)
    eng.state = {"board": board, "turn": turn, "turn_count": turn_count}
    return eng


# ══════════════════════════════════════════════════════════════════════════════
#  is_valid_move
# ══════════════════════════════════════════════════════════════════════════════

class TestIsValidMove:

    def test_legal_pawn_move_accepted(self):
        board = empty_board()
        board[3][2] = "wp"
        board[4][4] = "wK"
        board[0][0] = "bK"
        eng = engine_from_board(board, turn="white")
        assert eng.is_valid_move(((3, 2), (2, 2)))

    def test_illegal_pawn_move_rejected(self):
        board = empty_board()
        board[3][2] = "wp"
        board[4][4] = "wK"
        board[0][0] = "bK"
        eng = engine_from_board(board, turn="white")
        # Pawns cannot move backwards
        assert not eng.is_valid_move(((3, 2), (4, 2)))

    def test_wrong_turn_rejected(self):
        board = empty_board()
        board[3][2] = "wp"
        board[4][4] = "wK"
        board[0][0] = "bK"
        eng = engine_from_board(board, turn="black")   # black's turn
        assert not eng.is_valid_move(((3, 2), (2, 2)))

    def test_empty_square_origin_rejected(self):
        board = empty_board()
        board[4][4] = "wK"
        board[0][0] = "bK"
        eng = engine_from_board(board, turn="white")
        assert not eng.is_valid_move(((2, 2), (2, 3)))

    def test_out_of_bounds_origin_rejected(self):
        eng = GameEngine()
        assert not eng.is_valid_move(((9, 9), (0, 0)))

    def test_moving_opponent_piece_rejected(self):
        board = empty_board()
        board[1][2] = "bp"
        board[4][4] = "wK"
        board[0][0] = "bK"
        eng = engine_from_board(board, turn="white")
        assert not eng.is_valid_move(((1, 2), (2, 2)))


# ══════════════════════════════════════════════════════════════════════════════
#  is_game_over
# ══════════════════════════════════════════════════════════════════════════════

class TestIsGameOver:

    def test_no_game_over_at_start(self):
        eng = GameEngine()
        assert eng.is_game_over() is None

    def test_white_king_captured_black_wins(self):
        board = empty_board()
        board[0][0] = "bK"          # only black king
        eng = engine_from_board(board)
        result = eng.is_game_over()
        assert result is not None
        assert "Black" in result

    def test_black_king_captured_white_wins(self):
        board = empty_board()
        board[4][4] = "wK"          # only white king
        eng = engine_from_board(board)
        result = eng.is_game_over()
        assert result is not None
        assert "White" in result

    def test_max_turns_draw(self):
        board = empty_board()
        board[4][4] = "wK"
        board[0][0] = "bK"
        eng = engine_from_board(board, turn_count=10, max_turns=10)
        result = eng.is_game_over()
        assert result is not None
        assert "Draw" in result

    def test_below_max_turns_not_over(self):
        board = empty_board()
        board[4][4] = "wK"
        board[0][0] = "bK"
        eng = engine_from_board(board, turn_count=9, max_turns=10)
        assert eng.is_game_over() is None


# ══════════════════════════════════════════════════════════════════════════════
#  apply_move
# ══════════════════════════════════════════════════════════════════════════════

class TestApplyMove:

    def test_piece_moves_to_destination(self):
        board = empty_board()
        board[3][2] = "wp"
        board[4][4] = "wK"
        board[0][0] = "bK"
        eng = engine_from_board(board, turn="white")
        eng.apply_move(((3, 2), (2, 2)))
        assert eng.state["board"][2][2] == "wp"
        assert eng.state["board"][3][2] == "."

    def test_turn_switches_after_move(self):
        board = empty_board()
        board[3][2] = "wp"
        board[4][4] = "wK"
        board[0][0] = "bK"
        eng = engine_from_board(board, turn="white")
        eng.apply_move(((3, 2), (2, 2)))
        assert eng.state["turn"] == "black"

    def test_turn_count_increments(self):
        board = empty_board()
        board[3][2] = "wp"
        board[4][4] = "wK"
        board[0][0] = "bK"
        eng = engine_from_board(board, turn="white", turn_count=0)
        eng.apply_move(((3, 2), (2, 2)))
        assert eng.state["turn_count"] == 1

    def test_capture_removes_opponent_piece(self):
        board = empty_board()
        board[3][2] = "wp"
        board[2][1] = "bp"          # capturable diagonal
        board[4][4] = "wK"
        board[0][0] = "bK"
        eng = engine_from_board(board, turn="white")
        eng.apply_move(((3, 2), (2, 1)))
        assert eng.state["board"][2][1] == "wp"

    def test_white_pawn_promotes_at_row_0(self):
        board = empty_board()
        board[1][2] = "wp"          # one step from promotion
        board[4][4] = "wK"
        board[0][0] = "bK"
        eng = engine_from_board(board, turn="white")
        eng.apply_move(((1, 2), (0, 2)))
        assert eng.state["board"][0][2] == "wQ"

    def test_black_pawn_promotes_at_row_4(self):
        board = empty_board()
        board[3][2] = "bp"
        board[4][4] = "wK"
        board[0][0] = "bK"
        eng = engine_from_board(board, turn="black")
        eng.apply_move(((3, 2), (4, 2)))
        assert eng.state["board"][4][2] == "bQ"


# ══════════════════════════════════════════════════════════════════════════════
#  valid_moves_for_state / apply_move_to_state / is_game_over_for_state
#  (state-based variants used by the search tree)
# ══════════════════════════════════════════════════════════════════════════════

class TestStateVariants:

    def _simple_state(self, turn="white"):
        board = empty_board()
        board[3][2] = "wp"
        board[4][4] = "wK"
        board[0][0] = "bK"
        return {"board": board, "turn": turn, "turn_count": 0}

    def test_valid_moves_for_state_does_not_mutate_engine_state(self):
        eng = GameEngine()
        original = copy.deepcopy(eng.state)
        state = self._simple_state()
        eng.valid_moves_for_state(state)
        assert eng.state == original

    def test_apply_move_to_state_mutates_only_given_state(self):
        eng = GameEngine()
        original_board = copy.deepcopy(eng.state["board"])
        state = self._simple_state()
        eng.apply_move_to_state(state, ((3, 2), (2, 2)))
        # engine.state must be untouched
        assert eng.state["board"] == original_board
        # the passed state must be updated
        assert state["board"][2][2] == "wp"

    def test_is_game_over_for_state_white_king_missing(self):
        eng = GameEngine()
        state = {"board": empty_board(), "turn": "white", "turn_count": 0}
        state["board"][0][0] = "bK"
        assert eng.is_game_over_for_state(state) is not None

    def test_is_game_over_for_state_within_max_turns(self):
        eng = GameEngine(max_turns=50)
        state = self._simple_state()
        state["turn_count"] = 25
        assert eng.is_game_over_for_state(state) is None

    def test_is_game_over_for_state_at_max_turns(self):
        eng = GameEngine(max_turns=10)
        state = self._simple_state()
        state["turn_count"] = 10
        result = eng.is_game_over_for_state(state)
        assert result is not None and "Draw" in result
