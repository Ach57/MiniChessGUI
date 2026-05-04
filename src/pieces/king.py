def king_moves(position:tuple, game_state:dict)->list[tuple]:
    """_summary_
    Returns all possible moves for a King.
    Args:
        position (tuple): position of the piece in the board
        game_state (dict): Dictionary containing the board and turn
    """
    
    row,  col = position
    board = game_state["board"]
    turn = game_state["turn"]
    
    rows, cols = len(board), len(board[0])
    
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),         (0, 1),
                  (1, -1), (1, 0), (1, 1)]
    
    moves = []
    
    for dx, dy in directions:
        new_x, new_y = dx + row, dy+ col
        if 0 <= new_x < rows and 0 <= new_y < cols:
            target_piece = board[new_x][new_y]
            if target_piece =="." or ( target_piece and target_piece[0]!= turn[0]):
                moves.append((new_x, new_y))
    
    return moves


    
    
    
    
'''
(y)
|             possible moves for (0,0) = [(-1, -1),
|                                (-1, 0), (-1, 1), (0, -1),
|                                (0, 1), (1, -1), (1, 0), (1, 1)]
|
|
|
(0,0)---------------------- (x)
'''
        