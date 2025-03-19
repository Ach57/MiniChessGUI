import tkinter as tk
from tkinter import messagebox
from pieces.king import king_moves
from pieces.queen import queen_moves
from pieces.knight import knight_moves
from pieces.pawn import pawn_moves, promote_pawn
from pieces.bishop import bishop_moves
from mini_chess_logger import MiniChessLogger

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

class ChessGUI:
    def __init__(self, root):
        
        
        self.root = root
        self.root.title("Mini Chess Game")
        
        self.headerLabel = tk.Label(master=self.root, text='Welcome to Mini Chess Game', font = ('Arial', 36))
        self.headerLabel.grid(row = 0, columnspan=5)
        
        self.buttons = [[None for _ in range(5)] for _ in range(5)]
        self.selected_piece = None
        self.turnLabel = tk.Label(master=self.root, text = "", font = ('Arial', 24))
        self.create_board()
        
    
    def create_board(self):
        for i in range(5):
            for j in range(5):
                piece = state["board"][i][j]
                btn = tk.Button(self.root, text=PIECES[piece], font=("Arial", 36), highlightbackground='white',
                                width=4, height=2, command=lambda x=i, y=j: self.on_click(x, y))
                btn.grid(row=i+1, column=j)
                self.buttons[i][j] = btn
        self.turnLabel.config(text = f"{state['turn'].upper()} TURN")
        self.turnLabel.grid(row = 6, columnspan=5)
        

    def on_click(self, x, y):
        """Handles piece selection and movement."""
        piece = state["board"][x][y]
        
        if self.selected_piece is None:
            # Select piece if it belongs to the current player
            if piece.startswith(state["turn"][0]): 
                self.selected_piece = (x, y)
                self.buttons[x][y].config(highlightbackground = "gray")
            else:
                if piece !=".":
                    messagebox.showerror('Error', 'You can\'t move your opponenet\'s piece') 
        else:
            # Move piece
            old_x, old_y = self.selected_piece
            if old_x == x and old_y == y:
                self.buttons[x][y].config(highlightbackground = "white")
                self.selected_piece = None
                return
            is_move_valid = self.is_valid_move(game_state=state,move=((old_x, old_y), (x,y)) )
            if(is_move_valid):    
                piece = state["board"][old_x][old_y]
                captured_piece = state['board'][x][y]
                state["board"][x][y] = state["board"][old_x][old_y]
                state["board"][old_x][old_y] = "."
                
                if captured_piece == 'wK':
                    self.update_board(message=  "Black wins! White's King is captured.")
                    self.disable_buttons()
                    return
                    
                elif captured_piece =="bK":
                    
                    self.update_board(message="White Wins! Black\'s King is captured.")
                    self.disable_buttons()
                    return
                    
                if piece in ['wp','bp']: # check for promoting piece
                    promote_pawn((x,y), game_state = state)
            
                # Reset board colors and update UI
                self.selected_piece = None
                # Change turn
                state["turn"] = "white" if state["turn"] == "black" else "black"
                self.update_board(f"{state['turn'].upper()} TURN")
            else:
                messagebox.showwarning('Warning', 'Illegal Move!')

    def update_board(self, message:str):
        """Refreshes the board UI."""
        for i in range(5):
            for j in range(5):
                piece = state["board"][i][j]
                self.buttons[i][j].config(text=PIECES[piece], highlightbackground="white")
        self.turnLabel.config(text =message)
    
    def disable_buttons(self): #end of game
        for i in range(5):
            for j in range(5):
                self.buttons[i][j].config(state = tk.DISABLED)
    
        
    """
    Check if the move is valid    
    
    Args: 
        - game_state:   dictionary | Dictionary representing the current game state
        - move          tuple | the move which we check the validity of ((start_row, start_col),(end_row, end_col))
    Returns:
        - boolean representing the validity of the move
    """
    def is_valid_move(self, game_state, move):
        current_pos, destination = move
        board = game_state['board']
        turn = game_state['turn']
        try: # for when the player enters a move completely out of the board
            player = board[current_pos[0]][current_pos[1]]
        except IndexError:
            return False

        if player =='.':
            return False
        
        if (player[0] =='w' and turn!= 'white') or (player[0]=='b' and turn!='black'):
            return False
        
        valid_movements = self.valid_moves(game_state)
        
        if (current_pos, destination) in valid_movements:
            return True
        
        return False
    
    """
    Returns a list of valid moves

    Args:
        - game_state:   dictionary | Dictionary representing the current game state
    Returns:
        - valid moves:   list | A list of nested tuples corresponding to valid moves [((start_row, start_col),(end_row, end_col)),((start_row, start_col),(end_row, end_col))]
    """
    def valid_moves(self, game_state):
        board = game_state['board']
        turn = game_state['turn']
        valid_moves = []
        
        movement_rules = {
            "K": king_moves,
            "Q": queen_moves,
            "B": bishop_moves,
            "N": knight_moves,
            "p": pawn_moves
        }
        for row in range(5):
            for col in range(5):
                piece = board[row][col]
                if piece == ".": continue
                
                piece_color = "white" if piece[0] =="w" else "black"
                piece_type = piece[1]
                
                if piece_color == turn:
                    move_function = movement_rules.get(piece_type, lambda position, game_state: [])
                    possible_moves = move_function((row, col), game_state)
                    
                    for move in possible_moves:
                        end_row, end_col = move
                        if 0 <= end_row < 5 and 0 <= end_col < 5:
                            valid_moves.append(((row, col), (end_row, end_col)))
                
        return valid_moves
    


if __name__ =="__main__":
    # Run Tkinter GUI
    root = tk.Tk()
    game = ChessGUI(root)
    root.mainloop()
