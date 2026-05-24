"""
Unit tests for MiniChessLogger — singleton behaviour, notation helpers,
and branching-factor calculation.
File I/O is redirected to a tmp_path so tests leave no side-effects.
"""
import pytest
from pathlib import Path
from unittest.mock import patch

from src.Logger.mini_chess_logger import MiniChessLogger


# ── fixture: reset singleton before every test ────────────────────────────────

@pytest.fixture(autouse=True)
def reset_singleton(tmp_path, monkeypatch):
    """
    Guarantee a clean singleton slate for each test.
    Log files are written to pytest's tmp_path so they never pollute the repo.
    """
    MiniChessLogger._instance = None
    # Redirect log files to a temp directory
    monkeypatch.chdir(tmp_path)
    yield
    MiniChessLogger._instance = None


def _configure(**kwargs) -> MiniChessLogger:
    """Helper: configure the singleton with sensible defaults."""
    defaults = dict(
        alpha_beta=False,
        timeout=5,
        max_turns=50,
        player1_type="Human",
        player2_type="Human",
    )
    defaults.update(kwargs)
    return MiniChessLogger.configure(**defaults)


# ══════════════════════════════════════════════════════════════════════════════
#  Singleton behaviour
# ══════════════════════════════════════════════════════════════════════════════

class TestSingleton:

    def test_get_instance_before_configure_raises(self):
        with pytest.raises(RuntimeError, match="configure"):
            MiniChessLogger.get_instance()

    def test_configure_returns_instance(self):
        instance = _configure()
        assert isinstance(instance, MiniChessLogger)

    def test_get_instance_returns_same_object(self):
        _configure()
        a = MiniChessLogger.get_instance()
        b = MiniChessLogger.get_instance()
        assert a is b

    def test_configure_twice_overwrites_instance(self):
        first  = _configure(player1_type="Human")
        second = _configure(player1_type="AI", heuristic1="e0")
        assert MiniChessLogger.get_instance() is second
        assert MiniChessLogger.get_instance() is not first


# ══════════════════════════════════════════════════════════════════════════════
#  Move notation helper
# ══════════════════════════════════════════════════════════════════════════════

class TestFormatMove:

    def test_top_left_to_adjacent(self):
        # (0,0) → col A, row 5;  (1,0) → col A, row 4
        result = MiniChessLogger._format_move(((0, 0), (1, 0)))
        assert result == "A5 to A4"

    def test_bottom_right_to_centre(self):
        # (4,4) → col E, row 1;  (2,2) → col C, row 3
        result = MiniChessLogger._format_move(((4, 4), (2, 2)))
        assert result == "E1 to C3"

    def test_same_row_different_col(self):
        # (2,0) → col A, row 3;  (2,4) → col E, row 3
        result = MiniChessLogger._format_move(((2, 0), (2, 4)))
        assert result == "A3 to E3"

    def test_notation_contains_to_separator(self):
        result = MiniChessLogger._format_move(((0, 0), (0, 1)))
        assert " to " in result


# ══════════════════════════════════════════════════════════════════════════════
#  Branching factor
# ══════════════════════════════════════════════════════════════════════════════

class TestComputeBranchingFactor:

    def test_empty_dict_returns_zero(self):
        assert MiniChessLogger._compute_branching_factor({}) == 0.0

    def test_single_depth_returns_zero(self):
        assert MiniChessLogger._compute_branching_factor({0: 10}) == 0.0

    def test_two_depths_correct_average(self):
        # depth 0 → 1 node, depth 1 → 4 nodes → branching factor = 4/1 = 4.0
        result = MiniChessLogger._compute_branching_factor({0: 1, 1: 4})
        assert result == pytest.approx(4.0)

    def test_three_depths(self):
        # depth 0: 1, depth 1: 3, depth 2: 9
        # parents = 1 + 3 = 4; children = 3 + 9 = 12; bf = 12/4 = 3.0
        result = MiniChessLogger._compute_branching_factor({0: 1, 1: 3, 2: 9})
        assert result == pytest.approx(3.0)


# ══════════════════════════════════════════════════════════════════════════════
#  File output
# ══════════════════════════════════════════════════════════════════════════════

class TestFileOutput:

    def test_log_file_created_on_configure(self, tmp_path):
        _configure(alpha_beta=False, timeout=5, max_turns=50)
        log_files = list(tmp_path.glob("gameTrace-*.txt"))
        assert len(log_files) == 1

    def test_log_winner_writes_to_file(self, tmp_path):
        inst = _configure()
        inst.log_winner("White")
        log_file = next(tmp_path.glob("gameTrace-*.txt"))
        content = log_file.read_text(encoding="utf-8")
        assert "White" in content

    def test_log_move_increments_move_count(self):
        inst = _configure()
        assert inst._move_count == 0
        inst.log_move("white", ((3, 2), (2, 2)))
        assert inst._move_count == 1
        inst.log_move("black", ((1, 2), (2, 2)))
        assert inst._move_count == 2

    def test_invalid_move_does_not_increment_count(self):
        inst = _configure()
        inst.log_move("white", ((3, 2), (2, 2)), valid=False)
        assert inst._move_count == 0

    def test_header_written_to_file(self, tmp_path):
        _configure(alpha_beta=True, timeout=10, max_turns=100,
                   player1_type="AI", player2_type="Human", heuristic1="e1")
        log_file = next(tmp_path.glob("gameTrace-*.txt"))
        content = log_file.read_text(encoding="utf-8")
        assert "Alpha-Beta Pruning" in content
        assert "Mini Chess Game Trace" in content
