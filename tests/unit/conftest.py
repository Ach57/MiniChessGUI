"""
Shared fixtures for unit tests.
All board helpers build minimal 5×5 states so tests stay self-contained
and independent of GameConstants.
"""
import copy
import pytest


# ── board helpers ──────────────────────────────────────────────────────────────

def empty_board() -> list[list[str]]:
    """Return a 5×5 board with every square empty."""
    return [["." for _ in range(5)] for _ in range(5)]


def make_state(board: list[list[str]], turn: str = "white", turn_count: int = 0) -> dict:
    """Wrap a raw board into the game-state dict shape the engine/pieces expect."""
    return {"board": board, "turn": turn, "turn_count": turn_count}


# ── reusable fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def blank_state():
    """Completely empty board, white to move."""
    return make_state(empty_board())


@pytest.fixture
def starting_state():
    """Standard Mini-Chess opening position (matches GameConstants.state)."""
    board = [
        ["bK", "bQ", "bB", "bN", "."],
        [".",  ".",  "bp", "bp", "."],
        [".",  ".",  ".",  ".",  "."],
        [".",  "wp", "wp", ".",  "."],
        [".",  "wN", "wB", "wQ", "wK"],
    ]
    return make_state(board, turn="white", turn_count=0)
