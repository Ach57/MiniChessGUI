def pawn_moves(position: tuple, game_state: dict) -> list[tuple]: 
    """
    Args:
        position (tuple): position of the piece in the board
        game_state (dict): Dictionary containing the board and turn

    Returns:
        list[tuple]: possible moves
    """
    row, col = position  # Correctly treating position as (row, col)
    board = game_state["board"]
    turn = game_state["turn"]
    
    direction = -1 if turn == "white" else 1  # White moves up (-1), Black moves down (+1)
    moves = []

    # Move forward if the square is empty
    if 0 <= row + direction < 5 and board[row + direction][col] == ".":
        moves.append((row + direction, col))

    # Capture diagonally if there's an opponent piece
    for dc in [-1, 1]:  # Diagonal left and right
        if 0 <= col + dc < 5 and 0 <= row + direction < 5:
            target_piece = board[row + direction][col + dc]
            if target_piece != "." and target_piece[0] != turn[0]:  # Opponent's piece
                moves.append((row + direction, col + dc))

    return moves


def promote_pawn(position: tuple, game_state: dict):
    """Promotes a pawn to a queen if it reaches the last rank."""
    row, col = position
    board = game_state["board"]
    turn = game_state["turn"]
    
    if (row == 0 and turn == "white") or (row == 4 and turn == "black"):
        board[row][col] = "wQ" if turn == "white" else "bQ"