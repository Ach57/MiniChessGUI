'''-------------  GUI Libraries ----------------'''
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
'''-----------------------------------------------------'''

'''-------------  Pieces Configuration ----------------'''
from pieces.king import king_moves
from pieces.queen import queen_moves
from pieces.knight import knight_moves
from pieces.pawn import pawn_moves, promote_pawn
from pieces.bishop import bishop_moves

'''-----------------------------------------------------'''

import logging
import colorlog

class Logger:
    def __init__(self, logger_name = "my_logger", log_file = "miniChess.log"):
        
        # Create Logger
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        
        self._create_file_handler(log_file)
        self._create_terminal_handler()
        
    def _create_file_handler(self, log_file:str):
        """Creates and adds a file handler to the logger."""
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Log everything to the file
        file_formatter = logging.Formatter(
                '%(asctime)s - [%(levelname)s] - %(message)s',
                 datefmt='%Y-%m-%d %H:%M:%S'
                    )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
    def _create_terminal_handler(self):
        """Creates and adds a terminal handler with color support to the logger."""
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)  # Ensure this is set to DEBUG

        colored_formatter = colorlog.ColoredFormatter(
            "%(log_color)s[%(asctime)s] - [%(levelname)s] - %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )
        stream_handler.setFormatter(colored_formatter)
        self.logger.addHandler(stream_handler)

    def get_logger(self):
        """Returns the logger instance."""
        return self.logger

custom_logger = Logger().get_logger()
        

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

class Menu:
    def __init__(self, root: tk.Tk):
        
        self.root = root
        self.root.title("Mini Chess Game")

        self.headerlabel = tk.Label(root, text="Welcome to Mini Chess Game", font=('Arial', 24))
        self.headerlabel.grid(row=0, column=0, columnspan=2, pady=20)

        # Game mode selection
        self.mode_label = tk.Label(root, text="Choose game mode:", font=('Arial', 14))
        self.mode_label.grid(row=1, column=0, sticky="e")

        self.mode_var = tk.StringVar()
        self.mode_var.set("Select a mode...")
        self.mode_options = ["Player vs Player", "Player vs AI", "AI vs Player", "AI vs AI", "Exit"]
        self.mode_dropdown = ttk.Combobox(root, textvariable=self.mode_var, values=self.mode_options, state="readonly")
        self.mode_dropdown.grid(row=1, column=1, padx=10)
        self.mode_dropdown.bind("<<ComboboxSelected>>", self.show_ai_options)

        # Max time
        self.max_time_label = tk.Label(root, text="Max Time (sec):", font=('Arial', 12))
        self.max_time_entry = tk.Entry(root)

        # Max turns
        self.max_turns_label = tk.Label(root, text="Max Turns:", font=('Arial', 12))
        self.max_turns_entry = tk.Entry(root)

        # Heuristic
        self.heuristic_label = tk.Label(root, text="Heuristic (e0, e1, e2):", font=('Arial', 12))
        self.heuristic_var = tk.StringVar()
        self.heuristic_var.set("Select a Heuristic ...")
        self.heuristic_dropdown = ttk.Combobox(root, textvariable=self.heuristic_var, values=["e0", "e1", "e2"], state="readonly")

        # Alpha-beta
        self.alpha_beta_var = tk.BooleanVar()
        self.alpha_beta_check = tk.Checkbutton(root, text="Enable Alpha-Beta Pruning", variable=self.alpha_beta_var, font=('Arial', 12))

        # Start button
        self.start_button = tk.Button(root, text="Start Game", font=('Arial', 14), command=self.start_game)
        self.start_button.grid(row=10, column=0, columnspan=2, pady=20)            
                
    def show_ai_options(self, event=None):
        mode = self.mode_var.get()
        # Clear old options
        for widget in [self.max_time_label, self.max_time_entry,
                       self.max_turns_label, self.max_turns_entry,
                       self.heuristic_label, self.heuristic_dropdown,
                       self.alpha_beta_check]:
            widget.grid_remove()
            
        if "AI" in mode:
            self.max_time_label.grid(row=2, column=0, sticky="e")
            self.max_time_entry.grid(row=2, column=1, pady=5)
            
            self.max_turns_label.grid(row=3, column=0, sticky="e")
            self.max_turns_entry.grid(row=3, column=1, pady=5)

            self.heuristic_label.grid(row=4, column=0, sticky="e")
            self.heuristic_dropdown.grid(row=4, column=1, pady=5)

            self.alpha_beta_check.grid(row=5, column=0, columnspan=2, pady=5)

        elif mode == "Player vs Player":
            self.max_turns_label.grid(row=3, column=0, sticky="e")
            self.max_turns_entry.grid(row=3, column=1, pady=5)
            
    def start_game(self):
        mode = self.mode_var.get() 
        if mode =="Exit":
            custom_logger.info("Game Existed")
            self.root.quit()
        else:
            max_turn = self.max_turns_entry.get()
            custom_logger.info(f"max_turn set = {max_turn}")
            
            if mode == "Player vs Player": # Start player vs player
                self.root.destroy()
                root = tk.Tk()
                game = ChessGUI(root, player1="Player", player2="Player")
                root.mainloop()
            if "AI" in mode:
                max_time = self.max_time_entry.get()
                heuristic = self.heuristic_var.get()
                alpha_beta = self.alpha_beta_var.get()
                custom_logger.info(f"max_time: {max_time}, heuristic: {heuristic}, alpha_beta: {alpha_beta}")
                if mode =="Player vs AI":
                    self.root.destroy()
                    root = tk.Tk()
                    game = playerVsAi(root)
                    root.mainloop()
                

class playerVsAi:
    def __init__(self, root:tk.Tk):
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
                piece = state['board'][i][j]
                btn = tk.Button(self.root, text=PIECES[piece], font = ("Arial", 36), highlightbackground="white", 
                                width=4, height=2)
                btn.grid(row = i+1, column= j)
                self.buttons[i][j] = btn
            
            
        self.turnLabel.config(text = f"{state['turn'].upper()} TURN")
        self.turnLabel.grid(row = 6, columnspan=5)
    
    def on_click(self, x, y):
        piece = state['board'][x][y]# get the piece of the board
        return
        
        

class ChessGUI:
    def __init__(self, root: tk.Tk, player1: str, player2: str, heuristic: str = None, alpha_beta:bool = None):
        ''' Game Information '''
        self.player1= player1
        self.player2 = player2
        self.heuristic = heuristic
        self.alpha_beta = alpha_beta
        
        
        ''' GUI '''
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
    game = Menu(root)
    root.mainloop()
