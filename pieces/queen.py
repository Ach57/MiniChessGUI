def queen_moves(position:tuple, game_state: dict)->list[tuple]:
    """_summary_
    Returns all possible moves for a Queen.
    Args:
        position (tuple): position of the piece in the board
        game_state (dict): Dictionary containing the board and turn
    """
    
    row, col = position # get the row and col 
    board = game_state["board"]
    turn = game_state["turn"]
    
    
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),         (0, 1),
                  (1, -1), (1, 0), (1, 1)]
    
    moves = []
    
    for dx, dy in directions:
        for step in range(1, 5):  # Move as far as possible
            new_x, new_y = row + dx * step, col + dy * step
            if 0 <= new_x < 5 and 0 <= new_y < 5:
                target_piece = board[new_x][new_y]
                if target_piece=='.' or target_piece[0]!= turn[0]:
                    moves.append((new_x, new_y))
    
    return moves
