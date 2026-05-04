# Unicode symbols for pieces
PIECES = {
    "bK": "♚", "bQ": "♛", "bB": "♝", "bN": "♞", "bp": "♟",
    "wK": "♔", "wQ": "♕", "wB": "♗", "wN": "♘", "wp": "♙",
    ".": " "  # Empty spaces
}

# Initial game state
state = {
    "board": [
        ['bK', 'bQ', 'bB', 'bN', '.'],
        ['.', '.', 'bp', 'bp', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', 'wp', 'wp', '.', '.'],
        ['.', 'wN', 'wB', 'wQ', 'wK']
    ],
    "turn": 'white',
}