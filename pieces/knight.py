def knight_moves(position:tuple, game_state):
    """
    Args:
        position (tuple): position of the piece in the board
        game_state (dict): Dictionary containing the board and turn

    Returns:
        list[tuple]: possible moves
    """
    row, col = position
    board = game_state["board"]
    turn = game_state["turn"]
    
    moves = []
    directions = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                  (1, 2), (1, -2), (-1, 2), (-1, -2)]
    
    rows, cols = len(board), len(board[0])
    
    for dx, dy in directions:
        new_x, new_y = row + dx, col+ dy
        if 0 <= new_x < rows and 0 <= new_y < cols:
            target_piece = board[new_x][new_y]
            if target_piece == "." or ( target_piece and target_piece[0] !=turn[0]):
                moves.append((new_x,new_y))
    
    
    return moves
