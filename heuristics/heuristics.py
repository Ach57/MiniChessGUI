
def get_pieces_count(game_state: dict) ->dict:
    """_summary_
    Returns the number of pieces in a dictionary 
    Args:
        game_state (dict): game board 

    Returns:
        dict: number of pieces in a Dictionary
    """
    output_dict = {
        'black': {
                'K':0,
                'Q': 0,
                'B': 0,
                'N': 0,
                'p':0
            },
        'white':{
            'K':0,
            'Q': 0,
            'B': 0,
            'N': 0,
            'p':0
        }
    }
    board = game_state['board']# get the board
    
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] =='.':
                continue
            if board[row][col][0] =='b':
                output_dict['black'][board[row][col][1]]+=1
            else:
                output_dict['white'][board[row][col][1]]+=1
        
    return output_dict

def e0(pieces_count: dict, game_state:dict) -> int:
    """_summary_
    e0: Purely materialistic evaluation based on the count of each type of piece.
    Args:
        pieces_count (dict): dictionary contianing the piece count of black and white

    Returns:
        int: heuristic count
    """
    
    # Values for each piece type
    piece_values = {
        'p': 1,    # Pawn value
        'B': 3,    # Bishop value
        'N': 3,    # Knight value
        'Q': 9,    # Queen value
        'K': 999   # King value
    }

    # Get the pieces count for black and white
    black_values = pieces_count['black']
    white_values = pieces_count['white']

    # Calculate the total score for black and white
    black_count = sum(black_values[piece] * piece_values[piece] for piece in piece_values)
    white_count = sum(white_values[piece] * piece_values[piece] for piece in piece_values)

    # Return the difference (positive value favors white, negative favors black)
    return white_count - black_count


def e1(pieces_count: dict, game_state:dict) ->int:
    """_summary_
    e1: Material balance with added positional value. The position of pieces affects their overall score.
    Args:
        pieces_count (dict): _description_
        game_state (dict): _description_

    Returns:
        int: _description_
    """
    position_bonus = { # Requires adjustment
        'p': {  # Pawn positions based on them about to be promoted to Queen
            'black': [(3, 0), (3, 1), (3, 2), (3, 3), (3, 4)],  
            'white': [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)],  
        },
        'B': {  # Bishop positions
            'black': [(1, 1), (1, 3)],  
            'white': [(3, 1), (3, 3)], 
        },
        'N': {  # Knight positions
            'black': [(2,1), (2,3), (1,0), (1,4)],
            'white': [(2,1), (2,3), (3,0), (3,4)],

        },
        'Q': {  # Queen positions
        'black': [(2, 2)],  
            'white': [(2, 2)],   
        },
        'K': {  # King positions
            'black': [(0, 2)],  
            'white': [(4, 2)],  
        },
    }
    
    bonus_point_distribution = {
        'p': 10, # when the pawn is about to be promoted to queen
        'B': 4,
        "N": 4,
        "Q":9,
        "K": 8
    }
    
    def calculate_position_bonus(piece:str,color: str ,game_state:dict) ->int:
        """_summary_
        addes bonus points based on where each piece exists on the board
        Args:
            piece (str): ['p','B','N','Q','K']
            color (str): ['black','white']
            game_state (dict): dictionary

        Returns:
            int: bonus_point_distribution
        """
        
        bonus = 0
        board = game_state['board']
        
        favorable_position = position_bonus.get(piece, {}).get(color, [])

        for row, col in favorable_position:
            piece_at_position = board[row][col]
            if piece_at_position == ".":
                continue
            if piece_at_position[0] == color[0] and piece_at_position[1] == piece:
                if piece_at_position[0] =="w":
                    bonus+= bonus_point_distribution[piece]
                else:
                    bonus -= bonus_point_distribution[piece]
        return bonus
        
    score = e0(pieces_count, game_state)    
    white_position_score = 0
    black_position_score = 0
    for piece in ['p','B','N','Q','K']:
        white_position_score += calculate_position_bonus(piece = piece, color='white', game_state = game_state)
        black_position_score += calculate_position_bonus(piece=piece, color='black', game_state=game_state)
    
    return score + white_position_score+ black_position_score


def e2(piece_count: dict, game_state: dict ) ->int:
    """_summary_

    Args:
        piece_count (dict): use e0 to get the piece count
        game_state (dict): games state {board, turn}

    Returns:
        int: heuristic value
    """
    piece_capture_point = {
        'p': 2,    # Pawn value
        'B': 4,    # Bishop value
        'N': 4,    # Knight value
        'Q': 10,    # Queen value
        'K': 20   # King value
    }
    
    board = game_state['board']
    
    def get_caturing_pos_pawn(position:tuple, turn: str):
        moves = []
        row, col = position
        direction = -1 if turn == "w" else 1
        for dc in [-1,1]:
            if 0 <= col + dc < 5 and 0 <= row + direction < 5:
                target_piece = board[row+ direction][col+ dc]
                if target_piece!="." and target_piece[0] !=turn:
                    moves.append((row+direction, col+dc)) 
        return moves
    
    def get_capturing_pos_bishop(position: tuple, turn:str):
        moves = []
        x, y = position
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        rows, cols = len(board), len(board[0])
    
        for dx, dy in directions:
            for step in range(1, 5):
                new_x, new_y = x+dx*step, y+dy*step
                if 0<= new_x<rows and 0<= new_y<cols:
                    target_piece = board[new_x][new_y]
                    if target_piece !="." and target_piece[0] != turn[0]: # we shouldn't get the empty pos
                        moves.append((new_x, new_y))
                        break
                    elif target_piece!= ".":
                        break
        return moves
        
        
    def get_capturing_pos_knight(postion: tuple, turn: str):
        moves = []
        directions = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                  (1, 2), (1, -2), (-1, 2), (-1, -2)]
    
        rows, cols = len(board), len(board[0])
        row, col = postion
        for dx, dy in directions:
            new_x, new_y = row + dx, col+ dy
            if 0 <= new_x < rows and 0 <= new_y < cols:
                target_piece = board[new_x][new_y]
                if target_piece!='.' and target_piece[0] != turn:
                    moves.append((new_x,new_y))
                    
        return moves
    
    def get_capturing_pos_queen( position : tuple, turn: str):
        moves =  []
        row, col = position
        directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),         (0, 1),
                  (1, -1), (1, 0), (1, 1)]
        
        for dx, dy in directions:
            for step in range(1, 5):  # Move as far as possible
                new_x, new_y = row + dx * step, col + dy * step
                if 0 <= new_x < 5 and 0 <= new_y < 5:
                    target_piece = board[new_x][new_y]
                    if target_piece!='.' and target_piece[0]!= turn:
                        moves.append((new_x, new_y)) 
                        break
                    elif target_piece!= ".":
                        break
        return moves
    
    def get_capturing_pos_king(position: tuple, turn: str):
        row, col = position
        moves = []
        rows, cols = len(board), len(board[0])
        directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),         (0, 1),
                  (1, -1), (1, 0), (1, 1)]
        for dx, dy in directions:
            new_x, new_y = dx + row, dy+ col
            if 0 <= new_x < rows and 0 <= new_y < cols:
                target_piece = board[new_x][new_y]
                if target_piece!='.' and target_piece[0] !=turn:
                    moves.append((new_x, new_y))
        return moves
    
    score =e0(piece_count,game_state)
    points = 0 

    for row in range(len(board)):
        for col in range(len(board[row])):
            piece = board[row][col]
            if piece =='.':
                continue
            if piece[1] =="p":
                moves = get_caturing_pos_pawn(position=(row, col), turn= piece[0])
                if moves:
                    for x, y in moves:
                        capturing_piece = board[x][y]
                        points +=  piece_capture_point[capturing_piece[1]] if capturing_piece[0] =="b" else (-1) * piece_capture_point[capturing_piece[1]]
            
            elif piece[1] == "B":
                moves = get_capturing_pos_bishop(position=(row, col), turn= piece[1])
                if moves:
                    for x, y in moves:
                        capturing_piece = board[x][y]
                        points+= piece_capture_point[capturing_piece[1]] if capturing_piece[0] =="b" else (-1) * piece_capture_point[capturing_piece[1]]
            elif piece[1] =="N":
                moves = get_capturing_pos_knight(postion=(row, col), turn = piece[1])
                if moves:
                    for x, y in moves:
                        capturing_piece = board[x][y]
                        points += piece_capture_point[capturing_piece[1]] if capturing_piece[0] =="b" else (-1) * piece_capture_point[capturing_piece[1]]
            elif piece[1] =="Q":
                moves = get_capturing_pos_queen(position=(row, col), turn = piece[1])
                if moves:
                    for x, y in moves:
                        capturing_piece = board[x][y]
                        points += piece_capture_point[capturing_piece[1]] if capturing_piece[0] =="b" else (-1)*piece_capture_point[capturing_piece[1]]
            elif piece[1] =="K":
                moves = get_capturing_pos_king(position=(row, col), turn= piece[1])
                if moves:
                    for x, y in moves:
                        capturing_piece = board[x][y]
                        points+= piece_capture_point[capturing_piece[1]] if capturing_piece[0] =="b" else (-1)* piece_capture_point[capturing_piece[1]]
                        
    score+= points

    return score                
                
    