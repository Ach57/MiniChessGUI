"""
Unit tests for all piece-movement functions.

Board coordinates: (row, col) where (0,0) is top-left.
White moves UP  (decreasing row), Black moves DOWN (increasing row).
"""
import pytest
from tests.unit.conftest import empty_board, make_state

from src.pieces.pawn   import pawn_moves, promote_pawn
from src.pieces.knight import knight_moves
from src.pieces.bishop import bishop_moves
from src.pieces.king   import king_moves
from src.pieces.queen  import queen_moves


# ══════════════════════════════════════════════════════════════════════════════
#  PAWN
# ══════════════════════════════════════════════════════════════════════════════

class TestPawnMoves:

    def test_white_pawn_moves_forward_one(self):
        board = empty_board()
        board[3][2] = "wp"
        state = make_state(board, turn="white")
        assert (2, 2) in pawn_moves((3, 2), state)

    def test_black_pawn_moves_forward_one(self):
        board = empty_board()
        board[1][2] = "bp"
        state = make_state(board, turn="black")
        assert (2, 2) in pawn_moves((1, 2), state)

    def test_pawn_blocked_by_own_piece(self):
        board = empty_board()
        board[3][2] = "wp"
        board[2][2] = "wN"          # own piece directly ahead
        state = make_state(board, turn="white")
        assert pawn_moves((3, 2), state) == []

    def test_pawn_blocked_by_opponent_piece(self):
        board = empty_board()
        board[3][2] = "wp"
        board[2][2] = "bN"          # opponent directly ahead — not a capture
        state = make_state(board, turn="white")
        assert (2, 2) not in pawn_moves((3, 2), state)

    def test_white_pawn_captures_diagonally(self):
        board = empty_board()
        board[3][2] = "wp"
        board[2][1] = "bp"          # capturable diagonal left
        board[2][3] = "bp"          # capturable diagonal right
        state = make_state(board, turn="white")
        moves = pawn_moves((3, 2), state)
        assert (2, 1) in moves
        assert (2, 3) in moves

    def test_pawn_cannot_capture_own_piece_diagonally(self):
        board = empty_board()
        board[3][2] = "wp"
        board[2][1] = "wN"
        state = make_state(board, turn="white")
        assert (2, 1) not in pawn_moves((3, 2), state)

    def test_white_pawn_at_row_0_has_no_moves(self):
        board = empty_board()
        board[0][2] = "wp"
        state = make_state(board, turn="white")
        assert pawn_moves((0, 2), state) == []

    def test_black_pawn_at_row_4_has_no_moves(self):
        board = empty_board()
        board[4][2] = "bp"
        state = make_state(board, turn="black")
        assert pawn_moves((4, 2), state) == []

    def test_pawn_at_left_edge_no_left_capture(self):
        board = empty_board()
        board[3][0] = "wp"
        board[2][1] = "bp"          # only right diagonal exists on board
        state = make_state(board, turn="white")
        moves = pawn_moves((3, 0), state)
        assert (2, -1) not in moves   # left diagonal out of bounds

    def test_pawn_at_right_edge_no_right_capture(self):
        board = empty_board()
        board[3][4] = "wp"
        board[2][3] = "bp"
        state = make_state(board, turn="white")
        moves = pawn_moves((3, 4), state)
        assert all(0 <= c < 5 for _, c in moves)


class TestPromotePawn:

    def test_white_pawn_promoted_at_row_0(self):
        board = empty_board()
        board[0][2] = "wp"
        # After apply_move the turn has already flipped to black,
        # so promote_pawn is called while turn == "black" — but the piece
        # code itself drives promotion logic. Let's test the raw function:
        state = make_state(board, turn="white")
        promote_pawn((0, 2), state)
        assert board[0][2] == "wQ"

    def test_black_pawn_promoted_at_row_4(self):
        board = empty_board()
        board[4][2] = "bp"
        state = make_state(board, turn="black")
        promote_pawn((4, 2), state)
        assert board[4][2] == "bQ"

    def test_pawn_not_promoted_mid_board(self):
        board = empty_board()
        board[2][2] = "wp"
        state = make_state(board, turn="white")
        promote_pawn((2, 2), state)
        assert board[2][2] == "wp"   # unchanged


# ══════════════════════════════════════════════════════════════════════════════
#  KNIGHT
# ══════════════════════════════════════════════════════════════════════════════

class TestKnightMoves:

    def test_knight_centre_has_moves(self):
        board = empty_board()
        board[2][2] = "wN"
        state = make_state(board, turn="white")
        moves = knight_moves((2, 2), state)
        # From (2,2): all 8 L-shapes that land inside 5×5
        expected = {(0,1),(0,3),(1,0),(1,4),(3,0),(3,4),(4,1),(4,3)}
        assert set(moves) == expected

    def test_knight_corner_limited_moves(self):
        board = empty_board()
        board[0][0] = "wN"
        state = make_state(board, turn="white")
        moves = knight_moves((0, 0), state)
        # Only (1,2) and (2,1) are on the board
        assert set(moves) == {(1, 2), (2, 1)}

    def test_knight_cannot_land_on_own_piece(self):
        board = empty_board()
        board[2][2] = "wN"
        board[0][1] = "wQ"          # one of the L-shape targets
        state = make_state(board, turn="white")
        moves = knight_moves((2, 2), state)
        assert (0, 1) not in moves

    def test_knight_can_capture_opponent(self):
        board = empty_board()
        board[2][2] = "wN"
        board[0][1] = "bK"
        state = make_state(board, turn="white")
        moves = knight_moves((2, 2), state)
        assert (0, 1) in moves

    def test_knight_returns_only_valid_squares(self):
        board = empty_board()
        board[0][4] = "wN"
        state = make_state(board, turn="white")
        moves = knight_moves((0, 4), state)
        for r, c in moves:
            assert 0 <= r < 5 and 0 <= c < 5


# ══════════════════════════════════════════════════════════════════════════════
#  BISHOP
# ══════════════════════════════════════════════════════════════════════════════

class TestBishopMoves:

    def test_bishop_open_diagonal(self):
        board = empty_board()
        board[2][2] = "wB"
        state = make_state(board, turn="white")
        moves = bishop_moves((2, 2), state)
        # All 4 diagonal rays from centre on empty board
        expected = {(1,1),(0,0),(1,3),(0,4),(3,1),(4,0),(3,3),(4,4)}
        assert set(moves) == expected

    def test_bishop_blocked_by_own_piece(self):
        board = empty_board()
        board[2][2] = "wB"
        board[1][1] = "wQ"          # blocks upper-left ray after 1 step
        state = make_state(board, turn="white")
        moves = bishop_moves((2, 2), state)
        assert (1, 1) not in moves
        assert (0, 0) not in moves  # ray is fully blocked

    def test_bishop_captures_opponent_and_stops(self):
        board = empty_board()
        board[2][2] = "wB"
        board[1][1] = "bQ"
        state = make_state(board, turn="white")
        moves = bishop_moves((2, 2), state)
        assert (1, 1) in moves      # capture is legal
        assert (0, 0) not in moves  # cannot continue past capture

    def test_bishop_at_corner(self):
        board = empty_board()
        board[0][0] = "wB"
        state = make_state(board, turn="white")
        moves = bishop_moves((0, 0), state)
        # Only bottom-right diagonal is valid
        assert set(moves) == {(1,1),(2,2),(3,3),(4,4)}


# ══════════════════════════════════════════════════════════════════════════════
#  KING
# ══════════════════════════════════════════════════════════════════════════════

class TestKingMoves:

    def test_king_centre_has_8_moves(self):
        board = empty_board()
        board[2][2] = "wK"
        state = make_state(board, turn="white")
        moves = king_moves((2, 2), state)
        assert len(moves) == 8

    def test_king_corner_has_3_moves(self):
        board = empty_board()
        board[0][0] = "wK"
        state = make_state(board, turn="white")
        moves = king_moves((0, 0), state)
        assert set(moves) == {(0,1),(1,0),(1,1)}

    def test_king_cannot_move_to_own_piece(self):
        board = empty_board()
        board[2][2] = "wK"
        board[1][2] = "wQ"
        state = make_state(board, turn="white")
        moves = king_moves((2, 2), state)
        assert (1, 2) not in moves

    def test_king_can_capture_opponent(self):
        board = empty_board()
        board[2][2] = "wK"
        board[1][2] = "bQ"
        state = make_state(board, turn="white")
        moves = king_moves((2, 2), state)
        assert (1, 2) in moves

    def test_king_all_moves_on_board(self):
        for pos in [(0,0),(0,4),(4,0),(4,4),(2,2)]:
            board = empty_board()
            board[pos[0]][pos[1]] = "wK"
            state = make_state(board, turn="white")
            for r, c in king_moves(pos, state):
                assert 0 <= r < 5 and 0 <= c < 5


# ══════════════════════════════════════════════════════════════════════════════
#  QUEEN
# ══════════════════════════════════════════════════════════════════════════════

class TestQueenMoves:

    def test_queen_open_board_from_centre(self):
        board = empty_board()
        board[2][2] = "wQ"
        state = make_state(board, turn="white")
        moves = queen_moves((2, 2), state)
        # 4 straight rays + 4 diagonal rays from (2,2) on a 5×5 board
        assert len(moves) > 8

    def test_queen_blocked_by_own_piece(self):
        board = empty_board()
        board[2][2] = "wQ"
        board[2][3] = "wN"          # right neighbour
        state = make_state(board, turn="white")
        moves = queen_moves((2, 2), state)
        assert (2, 3) not in moves
        assert (2, 4) not in moves  # ray fully blocked

    def test_queen_captures_and_stops(self):
        board = empty_board()
        board[2][2] = "wQ"
        board[2][4] = "bK"
        state = make_state(board, turn="white")
        moves = queen_moves((2, 2), state)
        assert (2, 3) in moves      # empty square before target
        assert (2, 4) in moves      # capture square
        # no square beyond the board edge (5×5, so col 5 doesn't exist)

    def test_queen_combines_rook_and_bishop_directions(self):
        board = empty_board()
        board[0][0] = "wQ"
        state = make_state(board, turn="white")
        moves = set(queen_moves((0, 0), state))
        # Straight right along row 0
        assert (0, 1) in moves
        # Straight down along col 0
        assert (1, 0) in moves
        # Diagonal
        assert (1, 1) in moves

    def test_queen_all_moves_within_bounds(self):
        board = empty_board()
        board[2][2] = "wQ"
        state = make_state(board, turn="white")
        for r, c in queen_moves((2, 2), state):
            assert 0 <= r < 5 and 0 <= c < 5
