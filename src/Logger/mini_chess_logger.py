from __future__ import annotations
from .base_game_logger import BaseGameLogger

class MiniChessLogger(BaseGameLogger):
    _instance: MiniChessLogger | None = None

    # ------------------------------------------------------------------
    # Singleton interface
    # ------------------------------------------------------------------

    @classmethod
    def configure(
        cls,
        alpha_beta: bool,
        timeout: int,
        max_turns: int,
        player1_type: str,
        player2_type: str,
        heuristic1: str | None = None,
        heuristic2: str | None = None,
    ) -> MiniChessLogger:
        """Initialize the singleton. Call once from the menu before launching the game."""
        cls._instance = cls(
            alpha_beta=alpha_beta,
            timeout=timeout,
            max_turns=max_turns,
            player1_type=player1_type,
            player2_type=player2_type,
            heuristic1=heuristic1,
            heuristic2=heuristic2,
        )
        return cls._instance

    @classmethod
    def get_instance(cls) -> MiniChessLogger:
        """Return the configured singleton. Raises if configure() was not called first."""
        if cls._instance is None:
            raise RuntimeError(
                "MiniChessLogger is not configured. "
                "Call MiniChessLogger.configure(...) before get_instance()."
            )
        return cls._instance
    """
    Game trace logger for Mini Chess.
 
    Provides two output channels per event:
      - Terminal: concise colorized line via stdlib logging (info/warning/error)
      - Trace file: full structured entry via _write_to_file()
 
    Example:
        logger = MiniChessLogger(
            alpha_beta=True,
            timeout=5,
            max_turns=100,
            player1_type="AI",
            player2_type="Human",
            heuristic1="e1",
        )
        logger.log_board(game_state)
        logger.log_move("White", move, ai_time=0.42, heuristic_score=3)
        logger.log_winner("White")
    """
 
    def __init__(
        self,
        alpha_beta: bool,
        timeout: int,
        max_turns: int,
        player1_type: str,
        player2_type: str,
        heuristic1: str | None = None,
        heuristic2: str | None = None,
    ):
        self.alpha_beta = alpha_beta
        self.timeout = timeout
        self.max_turns = max_turns
        self.player1_type = player1_type
        self.player2_type = player2_type
        self.heuristic1 = heuristic1
        self.heuristic2 = heuristic2
        self._move_count = 0
 
        log_file = f"gameTrace-{str(alpha_beta).lower()}-{timeout}-{max_turns}.txt"
 
        # Must come last — super().__init__ calls _write_header(),
        # so all instance attributes above must exist first.
        super().__init__(logger_name="MiniChessLogger", log_file=log_file)
 
    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
 
    @staticmethod
    def _format_move(move: tuple) -> str:
        """Convert internal (row, col) tuples to chess notation e.g. 'B2 to B3'."""
        start, end = move
        return (
            f"{chr(ord('A') + start[1])}{5 - start[0]}"
            f" to "
            f"{chr(ord('A') + end[1])}{5 - end[0]}"
        )
 
    @staticmethod
    def _player_info(player_type: str, heuristic: str | None) -> str:
        """Format player descriptor for the trace file header."""
        if player_type == "AI" and heuristic:
            return f"AI (Alpha-Beta ON, Heuristic: {heuristic})"
        return player_type
 
    @staticmethod
    def _compute_branching_factor(depth_exploration: dict) -> float:
        """Calculate the average branching factor across all explored depths."""
        depths = sorted(depth_exploration)
        if len(depths) < 2:
            return 0.0
        total_expanded = sum(depth_exploration[d] for d in depths[1:])
        total_parents = sum(depth_exploration[d] for d in depths[:-1])
        return total_expanded / total_parents if total_parents else 0.0
 
    # ------------------------------------------------------------------
    # BaseGameLogger implementation
    # ------------------------------------------------------------------
 
    def _write_header(self) -> None:
        """Write game config to trace file + a single info line to terminal."""
        self.info("Mini Chess game trace initialized")
 
        for line in [
            "=" * 40,
            "Mini Chess Game Trace",
            "=" * 40,
            f"Alpha-Beta Pruning : {'ON' if self.alpha_beta else 'OFF'}",
            f"Timeout per move   : {self.timeout} seconds",
            f"Max turns          : {self.max_turns}",
            f"Player 1           : {self._player_info(self.player1_type, self.heuristic1)}",
            f"Player 2           : {self._player_info(self.player2_type, self.heuristic2)}",
            "",
            "Initial Board Configuration:",
        ]:
            self._write_to_file(line)
 
    def log_board(self, game_state: dict) -> None:
        """Write board grid to trace file (raw, no logging formatter)."""
        for row in game_state["board"]:
            self._write_to_file(" ".join(row))
        self._write_to_file("")
 
    def log_move(
        self,
        player: str,
        move: tuple,
        ai_time: float | None = None,
        heuristic_score: float | None = None,
        alpha_beta_score: float | None = None,
        mini_max_score: float | None = None,
        valid: bool = True,
    ) -> None:
        """
        Record a move to both output channels.
 
        Terminal  → concise single line (colorized via logging level)
        Trace file → full structured entry with optional AI stats
        """
        if not valid:
            self.warning(f"Invalid move by {player} at turn #{self._move_count}")
            self._write_to_file(f"Invalid move by {player} at turn #{self._move_count}\n")
            return
 
        self._move_count += 1
        move_str = self._format_move(move)
 
        # Terminal: one clean line
        self.info(f"Turn #{self._move_count:>3} | {player:<6} → {move_str}")
 
        # Trace file: full entry
        self._write_to_file(f"Turn #{self._move_count}: {player} moves {move_str}")
        if ai_time is not None:
            self._write_to_file(f"  AI move time       : {ai_time:.3f} sec")
        if heuristic_score is not None:
            self._write_to_file(f"  Heuristic Score    : {heuristic_score}")
        if mini_max_score is not None:
            self._write_to_file(f"  MiniMax Score      : {mini_max_score}")
        if alpha_beta_score is not None:
            self._write_to_file(f"  Alpha-Beta Score   : {alpha_beta_score}")
        self._write_to_file("")
 
    def log_ai_stats(self, states_explored: int, depth_exploration: dict) -> None:
        """
        Record cumulative AI search statistics.
 
        Terminal  → summary line only
        Trace file → full depth breakdown with percentages and branching factor
        """
        total = sum(depth_exploration.values())
        bf = self._compute_branching_factor(depth_exploration)
 
        # Terminal: summary
        self.info(
            f"AI Stats | States explored: {states_explored} | "
            f"Avg branching factor: {bf:.2f}"
        )
 
        # Trace file: full breakdown
        self._write_to_file("Cumulative AI Search Statistics:")
        self._write_to_file(f"  States Explored : {states_explored}")
        self._write_to_file("  By depth:")
        for depth, count in sorted(depth_exploration.items()):
            pct = (count / total * 100) if total else 0.0
            self._write_to_file(f"    Depth {depth}: {count:>6} states ({pct:.2f}%)")
        self._write_to_file(f"  Avg Branching Factor: {bf:.2f}")
        self._write_to_file("")
 
    def log_winner(self, winner: str) -> None:
        """Record the game result to both output channels."""
        turns = self._move_count // 2
 
        self.info(f"Game Over — {winner} wins in {turns} turns!")
 
        self._write_to_file("=" * 40)
        self._write_to_file(f"Game Over: {winner} wins in {turns} turns")
        self._write_to_file("=" * 40)
 
    def log_info(self, message: str) -> None:
        """Convenience method: write an arbitrary message to both channels."""
        self.info(message)
        self._write_to_file(message)
