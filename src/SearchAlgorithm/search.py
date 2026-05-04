import copy
import time
from heuristics.heuristics import get_pieces_count
from  collections import defaultdict

class SearchAlgorithm:
    def __init__(self, game, heuristic, alpha_beta:bool=True, max_time:int=5, maximizier:bool=True) ->None:
        """
        Initializes the search algorithm.
        
        Args:
            game: The MiniChess game instance.
            heuristic: The heuristic function to evaluate board states.
            alpha_beta (bool): Whether to use Alpha-Beta Pruning (True) or Minimax (False).
            max_time (int): Maximum time allowed for the AI to make a move.
        """
        self.game = game  # Reference to the MiniChess game
        self.heuristic = heuristic  # Chosen heuristic function
        self.alpha_beta = alpha_beta  # Boolean: True for Alpha-Beta, False for Minimax
        self.max_time = max_time  # Time limit for AI move computation
        self.start_time = None  # Track the start time for time management
        self.maximizer = maximizier
        self.cumulative_count = 0
        self.state_by_depth = defaultdict(int)
    
    def search_best_move(self, depth):
        """
        Decides whether to use Minimax or Alpha-Beta based on the `self.alpha_beta` flag.
        
        Args:
            depth (int): Maximum depth to search in the game tree.

        Returns:
            tuple: (best_score, best_move)
        """
        self.start_time = time.time()
        if self.alpha_beta: # If alpha beta activated
            move = self.alpha_beta_pruning(self.game,depth, float('-inf'), float('inf'), self.maximizer)
            end_time = time.time()
            time_spent = end_time -self.start_time
            return (move[0], move[1], time_spent) # heuristic score of the search, move, time_spent on the search
        else: 
            #return self.minimax(game_state=copy_state,depth = depth, maximizing_player=True) # Call for minimax with maximizing at the turn of the Ai
            move = self.minimax(self.game, depth, self.maximizer)
            end_time = time.time()
            time_spent = end_time - self.start_time #Get time spent on the search
            return (move[0], move[1], time_spent) # heuristic score of the search, move, time spent on the search
        

    def minimax(self, game_state , depth: int, maximizing_player: bool):
        if time.time() - self.start_time >= self.max_time:
            print("AI exceeded time limit! It loses.")
            self.game.logger.log_winner(f"{'White' if maximizing_player else 'Black'} loses due to timeout.")
            exit(1)
        
        if depth == 0 or self.game.is_game_over(): # check if we're at depth 0 or if the game is over or not
            self.cumulative_count+=1
            
            return self.evaluation_score(game_state), None # returns the heuristic score, best_move = none

        best_move = None
        valid_moves = game_state.valid_moves(game_state.current_game_state) # Get all valid moves of the current state
        
        if maximizing_player:
            max_eval = float("-inf")
            for move in valid_moves:
                new_state = copy.deepcopy(game_state)
                new_state.ai_make_move(new_state.current_game_state, move)
                self.state_by_depth[depth]+=1
                eval_score, _ = self.minimax(new_state, depth-1, False)
                
                if eval_score>max_eval:
                    max_eval = eval_score
                    best_move = move 
            
            return max_eval, best_move
        else:
            min_eval = float("+inf")
            for move in valid_moves:
                new_state = copy.deepcopy(game_state)
                new_state.ai_make_move(new_state.current_game_state, move)
                self.state_by_depth[depth]+=1
                eval_score, _ = self.minimax(new_state,depth-1, True)
                if eval_score< min_eval:
                    
                    min_eval = eval_score
                    best_move = move
                
            return min_eval, best_move 
        
    """
    Implements Alpha-Beta Pruning to optimize Minimax.
    
    Args:
        depth (int): How deep the search tree should go.
        alpha (float): Best already explored option along the path for the maximizer.
        beta (float): Best already explored option along the path for the minimizer.
        maximizing_player (bool): True if maximizing (White), False if minimizing (Black).

    Returns:
        tuple: (best_score, best_move)
    """
    def alpha_beta_pruning(self,game_state, depth, alpha, beta, maximizing_player):
        # Check if time is up before continuing the search
        if time.time() - self.start_time >= self.max_time:
            print("AI exceeded time limit! It loses.")
            self.game.logger.log_winner(f"{'White' if maximizing_player else 'Black'} loses due to timeout.")
            exit(0)  # AI automatically loses if it takes too long

        # Base case: If depth = 0 or game is over, evaluate the board.
        if depth == 0 or self.game.is_game_over():
            self.cumulative_count +=1
            return self.evaluation_score(game_state), None

        best_move = None
        valid_moves = game_state.valid_moves(game_state.current_game_state)

        if maximizing_player:  # White (Maximizing)
            max_eval = float('-inf')
            for move in valid_moves:
                new_state = copy.deepcopy(game_state)
                new_state.ai_make_move(new_state.current_game_state, move)
                self.state_by_depth[depth]+=1
                eval_score, _ = self.alpha_beta_pruning(new_state,depth - 1, alpha, beta, False)

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move

                # Alpha-Beta Pruning Condition
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Prune the remaining branches

            return max_eval, best_move

        else:  # Black (Minimizing)
            min_eval = float('inf')
            for move in valid_moves:
                new_state = copy.deepcopy(game_state)
                new_state.ai_make_move(new_state.current_game_state, move)
                self.state_by_depth[depth]+=1
                eval_score, _ = self.alpha_beta_pruning(new_state,depth - 1, alpha, beta, True)

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move

                # Alpha-Beta Pruning Condition
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Prune the remaining branches

            return min_eval, best_move
            
    def evaluation_score(self, current_state):
        """
        Evaluates the game state using the chosen heuristic.
        
        Returns:
            int: Heuristic score representing the favorability of the state.
        """
        heuristic_func = self.heuristic
        current_game_state = current_state.current_game_state
        return heuristic_func(get_pieces_count(current_game_state), current_game_state)
        
        
