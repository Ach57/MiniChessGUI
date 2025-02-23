def bishop_moves(position:tuple, game_state: dict)->list[tuple]:
    """
    Args:
        position (tuple): position of the piece in the board
        game_state (dict): Dictionary containing the board and turn

    Returns:
        list[tuple]: possible moves
    """
    
    x, y = position
    board = game_state["board"]
    turn = game_state["turn"]
    
    
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    moves = []
    
    rows, cols = len(board), len(board[0])
    
    for dx, dy in directions:
        for step in range(1, 5):  # Move as far as possible
            new_x, new_y = x + dx * step, y + dy * step
            if 0 <= new_x < rows and 0 <= new_y < cols:
                target_piece = board[new_x][new_y]
                if target_piece =="." or (target_piece and target_piece[0] !=turn[0]):
                    moves.append((new_x, new_y))
    return moves
    
    
