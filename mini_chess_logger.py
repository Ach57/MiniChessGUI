import time

class MiniChessLogger:
    def __init__(self, alpha_beta, timeout, max_turns):
        self.alpha_beta = alpha_beta  # Boolean for Alpha-Beta pruning
        self.timeout = timeout  # Max time per AI move
        self.max_turns = max_turns  # Max turns allowed in the game
        self.log_file = f"gameTrace-{str(alpha_beta).lower()}-{timeout}-{max_turns}.txt"
        self.move_count = 1
        self.states_explored = 0  # Track number of states explored by AI
        self.depth_exploration = {}  # Track states per depth
        self.start_logging()
    
    def start_logging(self):
        """Initialize the log file with game parameters."""
        with open(self.log_file, 'w') as file:
            file.write(f"Mini Chess Game Trace\n")
            file.write(f"Alpha-Beta Pruning: {'ON' if self.alpha_beta else 'OFF'}\n")
            file.write(f"Timeout per move: {self.timeout} seconds\n")
            file.write(f"Max turns: {self.max_turns}\n")
            file.write("\nInitial Board Configuration:\n")
    
    def log_board(self, game_state):
        """Log the board state after each move."""
        with open(self.log_file, 'a') as file:
            for row in game_state["board"]:
                file.write(' '.join(row) + "\n")
            file.write("\n")
    
    def log_move(self, player, move, ai_time=None, heuristic_score=None, alpha_beta_score=None, valid =False):
        """Log each move taken."""
        
        if not valid:
            with open(self.log_file, 'a') as file:
                file.write(f'Invalid move made by {player} at turn #{self.move_count}')
                file.write('\n')
            return
        self.move_count += 1
        with open(self.log_file, 'a') as file:
            file.write(f"Turn #{self.move_count}: {player} moves {move}\n")
            if ai_time is not None:
                file.write(f"AI move time: {ai_time:.2f} sec\n")
            if heuristic_score is not None:
                file.write(f"Heuristic Score: {heuristic_score}\n")
            if alpha_beta_score is not None:
                file.write(f"Alpha-Beta Score: {alpha_beta_score}\n")
            file.write("\n")
    
    def log_ai_stats(self):
        """Log AI search statistics (states explored, depth breakdown, branching factor)."""
        with open(self.log_file, 'a') as file:
            file.write("AI Search Statistics:\n")
            file.write(f"Total states explored: {self.states_explored}\n")
            for depth, count in self.depth_exploration.items():
                file.write(f"Depth {depth}: {count} states\n")
            avg_branch_factor = self.compute_branching_factor()
            file.write(f"Average Branching Factor: {avg_branch_factor:.2f}\n\n")
    
    def compute_branching_factor(self):
        """Calculate the average branching factor based on depth exploration data."""
        if len(self.depth_exploration) < 2:
            return 0
        depths = sorted(self.depth_exploration.keys())
        return sum(self.depth_exploration[d] for d in depths[1:]) / sum(self.depth_exploration[d] for d in depths[:-1])
    
    def log_winner(self, winner):
        """Log the winner at the end of the game."""
        with open(self.log_file, 'a') as file:
            file.write(f"Game Over: {winner} wins in {self.move_count} turns\n")
            file.write("\n")
            
    
