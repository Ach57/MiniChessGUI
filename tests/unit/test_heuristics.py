"""
Unit tests for heuristic functions: get_pieces_count, e0, e1, e2.
"""
import pytest
from tests.unit.conftest import empty_board, make_state

from src.heuristics.heuristics import get_pieces_count, e0, e1, e2


# ── helpers ────────────────────────────────────────────────────────────────────

def _kings_only(white_pos=(4, 4), black_pos=(0, 0)) -> dict:
    """Minimal state: only two kings on the board."""
    board = empty_board()
    board[white_pos[0]][white_pos[1]] = "wK"
    board[black_pos[0]][black_pos[1]] = "bK"
    return make_state(board)


# ══════════════════════════════════════════════════════════════════════════════
#  get_pieces_count
# ══════════════════════════════════════════════════════════════════════════════

class TestGetPiecesCount:

    def test_empty_board_all_zero(self):
        state = make_state(empty_board())
        counts = get_pieces_count(state)
        for color in ("white", "black"):
            for piece in ("K", "Q", "B", "N", "p"):
                assert counts[color][piece] == 0

    def test_starting_position_counts(self):
        board = [
            ["bK", "bQ", "bB", "bN", "."],
            [".",  ".",  "bp", "bp", "."],
            [".",  ".",  ".",  ".",  "."],
            [".",  "wp", "wp", ".",  "."],
            [".",  "wN", "wB", "wQ", "wK"],
        ]
        state = make_state(board)
        counts = get_pieces_count(state)
        assert counts["black"] == {"K": 1, "Q": 1, "B": 1, "N": 1, "p": 2}
        assert counts["white"] == {"K": 1, "Q": 1, "B": 1, "N": 1, "p": 2}

    def test_single_white_queen(self):
        board = empty_board()
        board[2][2] = "wQ"
        state = make_state(board)
        counts = get_pieces_count(state)
        assert counts["white"]["Q"] == 1
        assert counts["black"]["Q"] == 0

    def test_multiple_pieces_same_type(self):
        board = empty_board()
        board[0][0] = "bp"
        board[0][1] = "bp"
        board[0][2] = "bp"
        state = make_state(board)
        counts = get_pieces_count(state)
        assert counts["black"]["p"] == 3


# ══════════════════════════════════════════════════════════════════════════════
#  e0 — material heuristic
# ══════════════════════════════════════════════════════════════════════════════

class TestE0:

    def test_equal_material_returns_zero(self):
        state = _kings_only()
        counts = get_pieces_count(state)
        assert e0(counts, state) == 0

    def test_white_queen_advantage(self):
        board = empty_board()
        board[4][4] = "wK"
        board[0][0] = "bK"
        board[2][2] = "wQ"          # extra white queen
        state = make_state(board)
        counts = get_pieces_count(state)
        assert e0(counts, state) == 9   # queen = 9

    def test_black_queen_advantage_is_negative(self):
        board = empty_board()
        board[4][4] = "wK"
        board[0][0] = "bK"
        board[2][2] = "bQ"
        state = make_state(board)
        counts = get_pieces_count(state)
        assert e0(counts, state) == -9

    def test_pawn_value_is_one(self):
        board = empty_board()
        board[4][4] = "wK"
        board[0][0] = "bK"
        board[3][1] = "wp"
        state = make_state(board)
        counts = get_pieces_count(state)
        assert e0(counts, state) == 1

    def test_starting_position_is_balanced(self):
        board = [
            ["bK", "bQ", "bB", "bN", "."],
            [".",  ".",  "bp", "bp", "."],
            [".",  ".",  ".",  ".",  "."],
            [".",  "wp", "wp", ".",  "."],
            [".",  "wN", "wB", "wQ", "wK"],
        ]
        state = make_state(board)
        counts = get_pieces_count(state)
        assert e0(counts, state) == 0

    def test_piece_values_bishop_knight_equal(self):
        board = empty_board()
        board[4][4] = "wK"
        board[0][0] = "bK"
        board[2][2] = "wB"
        board[2][3] = "bN"
        state = make_state(board)
        counts = get_pieces_count(state)
        # wB=3, bN=3 → difference is 0
        assert e0(counts, state) == 0


# ══════════════════════════════════════════════════════════════════════════════
#  e1 — material + positional heuristic
# ══════════════════════════════════════════════════════════════════════════════

class TestE1:

    def test_equal_material_no_position_bonus_is_zero(self):
        """Kings only in non-bonus squares → no positional bonus, score = 0."""
        state = _kings_only(white_pos=(4, 0), black_pos=(0, 4))
        counts = get_pieces_count(state)
        assert e1(counts, state) == 0

    def test_white_pawn_in_bonus_position(self):
        """White pawn at row 1 earns a positional bonus on top of material."""
        board = empty_board()
        board[4][4] = "wK"
        board[0][0] = "bK"
        board[1][0] = "wp"          # row 1 is a white-pawn bonus row
        state = make_state(board)
        counts = get_pieces_count(state)
        score = e1(counts, state)
        # material: wp=1 → e0 = 1; bonus: pawn at bonus pos adds 10
        assert score > e0(counts, state)

    def test_e1_at_least_as_good_as_e0_for_white_advantage(self):
        board = empty_board()
        board[4][4] = "wK"
        board[0][0] = "bK"
        board[2][2] = "wQ"
        state = make_state(board)
        counts = get_pieces_count(state)
        assert e1(counts, state) >= e0(counts, state)


# ══════════════════════════════════════════════════════════════════════════════
#  e2 — capture-threat heuristic
# ══════════════════════════════════════════════════════════════════════════════

class TestE2:

    def test_no_captures_available_equals_e0(self):
        """Pieces that cannot capture anything → e2 equals e0."""
        state = _kings_only(white_pos=(4, 4), black_pos=(0, 0))
        counts = get_pieces_count(state)
        assert e2(counts, state) == e0(counts, state)

    def test_white_pawn_threatening_black_queen(self):
        """White pawn diagonally threatens a black queen → positive bonus."""
        board = empty_board()
        board[4][4] = "wK"
        board[0][0] = "bK"
        board[3][2] = "wp"
        board[2][1] = "bQ"          # white pawn captures diagonally
        state = make_state(board)
        counts = get_pieces_count(state)
        score = e2(counts, state)
        base  = e0(counts, state)
        assert score > base         # threat bonus applied

    def test_e2_returns_int(self):
        state = _kings_only()
        counts = get_pieces_count(state)
        result = e2(counts, state)
        assert isinstance(result, int)
