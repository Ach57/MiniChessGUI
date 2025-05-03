class MiniChessLogger:
    def __init__(self, alpha_beta, timeout, max_turns, player1_type, player2_type, heuristic1=None, heuristic2=None):
        """
        Initializes the logger.

        Args:
            alpha_beta (bool): Whether Alpha-Beta Pruning is enabled.
            timeout (int): Maximum time allowed per AI move.
            max_turns (int): Maximum number of turns in the game.
            player1_type (str): "AI" or "Human" for Player 1.
            player2_type (str): "AI" or "Human" for Player 2.
            heuristic1 (str, optional): AI heuristic for Player 1 (if applicable).
            heuristic2 (str, optional): AI heuristic for Player 2 (if applicable).
        """
        self.alpha_beta = alpha_beta
        self.timeout = timeout
        self.max_turns = max_turns
        self.log_file = f"gameTrace-{str(alpha_beta).lower()}-{timeout}-{max_turns}.txt"
        self.move_count = 0  # Track total moves
        self.player1_type = player1_type
        self.player2_type = player2_type
        self.heuristic1 = heuristic1
        self.heuristic2 = heuristic2
        self.start_logging()

    def start_logging(self):
        """Initialize the log file with game parameters."""
        with open(self.log_file, 'w') as file:
            file.write(f"Mini Chess Game Trace\n")
            file.write(f"Alpha-Beta Pruning: {'ON' if self.alpha_beta else 'OFF'}\n")
            file.write(f"Timeout per move: {self.timeout} seconds\n")
            file.write(f"Max turns: {self.max_turns}\n")
            file.write(f"Player 1: {self.player1_type} {'(Alpha-Beta ON, Heuristic: ' + self.heuristic1 + ')' if self.player1_type == 'AI' else ''}\n")
            file.write(f"Player 2: {self.player2_type} {'(Alpha-Beta ON, Heuristic: ' + self.heuristic2 + ')' if self.player2_type == 'AI' else ''}\n")
            file.write("\nInitial Board Configuration:\n")

    def log_board(self, game_state):
        """Log the board state after each move."""
        with open(self.log_file, 'a') as file:
            for row in game_state["board"]:
                file.write(' '.join(row) + "\n")
            file.write("\n")

    def log_move(self, player, move, ai_time=None, heuristic_score=None, alpha_beta_score=None, mini_max_score = None,valid=True):
        """Log each move taken by human or AI."""
        if valid: 
            self.move_count += 1  # Increment turn count

        with open(self.log_file, 'a') as file:
            if not valid:
                file.write(f"Invalid move made by {player} at turn #{self.move_count}\n")
                return

            # Format move (e.g., "B2 B3")
            start, end = move
            move_str = f"{chr(ord('A') + start[1])}{5 - start[0]} to {chr(ord('A') + end[1])}{5 - end[0]}"

            file.write(f"Turn #{self.move_count}: {player} moves {move_str}\n")

            if ai_time is not None:
                file.write(f"AI move time: {ai_time:.3f} sec\n")
            if heuristic_score is not None:
                file.write(f"Heuristic Score: {heuristic_score}\n")
            if mini_max_score is not None:
                file.write(f"MiniMax Search Score: {mini_max_score}\n")
            if alpha_beta_score is not None:
                file.write(f"Alpha-Beta Search Score: {alpha_beta_score}\n")

            file.write("\n")

    def log_ai_stats(self, states_explored:int, depth_exploration:dict):
        """Log AI search statistics (states explored, depth breakdown, branching factor)."""
        with open(self.log_file, 'a') as file:
            file.write("Cumulative AI Search Statistics:\n")
            file.write(f"Cumulative States Explored: {states_explored}\n")

            # Log exploration by depth
            file.write("Cumulative states explored by depth:\n")
            total_states = sum(depth_exploration.values())

            for depth, count in sorted(depth_exploration.items()):
                file.write(f"Depth {depth}: {count} states\n")

            # Log percentage of states explored per depth
            file.write("Cumulative % states explored by depth:\n")
            for depth, count in sorted(depth_exploration.items()):
                percentage = (count / total_states) * 100 if total_states > 0 else 0
                file.write(f"Depth {depth}: {percentage:.2f}%\n")

            # Log average branching factor
            avg_branch_factor = self.compute_branching_factor(depth_exploration)
            file.write(f"Average Branching Factor: {avg_branch_factor:.2f}\n\n")

    def compute_branching_factor(self, depth_exploration):
        """Calculate the average branching factor based on depth exploration data."""
        if len(depth_exploration) < 2:
            return 0

        depths = sorted(depth_exploration.keys())
        total_expanded = sum(depth_exploration[d] for d in depths[1:])
        total_parent_nodes = sum(depth_exploration[d] for d in depths[:-1])

        return total_expanded / total_parent_nodes if total_parent_nodes > 0 else 0

    def log_winner(self, winner):
        """Log the winner at the end of the game."""
        with open(self.log_file, 'a') as file:
            file.write(f"Game Over: {winner} wins in {self.move_count // 2} turns\n\n")
    
    def log_info(self, message: str):
        with open(self.log_file, "a") as file:
            file.write(message)
            file.write("\n")

