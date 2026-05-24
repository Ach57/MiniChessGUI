import logging
import colorlog
from abc import ABC, abstractmethod
from src.constants.setup import SetupConstants as SC


class BaseGameLogger(logging.Logger, ABC):
    """
    Abstract base logger for game trace logging.

    Extends logging.Logger directly so every subclass IS a fully functional
    stdlib logger — self.info(), self.debug(), self.warning() etc. all work
    natively with colorized terminal output.

    Adds a second raw-write channel (_write_to_file) for structured game
    trace output that bypasses the logging formatter (e.g. board grids,
    stats tables) where timestamps and level tags would pollute the output.

    Subclasses must implement:
        - _write_header()   called once on __init__ to open the trace file
        - log_move()        record a single move
        - log_board()       record a board state
        - log_winner()      record the final result

    Usage:
        # In your entry point, before any imports that use logging:
        logging.setLoggerClass(MiniChessLogger)
    """

    def __init__(self, logger_name: str, log_file: str):
        super().__init__(logger_name, logging.DEBUG)

        self._log_file = log_file

        # Guard against duplicate handlers if the logger name is reused
        if not self.handlers:
            self._add_file_handler(log_file)
            self._add_terminal_handler()

        self._write_header()

    # ------------------------------------------------------------------
    # Handler setup
    # ------------------------------------------------------------------

    def _add_file_handler(self, log_file: str) -> None:
        """Attach a file handler for structured logging output."""
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s - [%(levelname)s] - %(message)s",
            datefmt=SC.DATE_FORMAT
        ))
        self.addHandler(handler)

    def _add_terminal_handler(self) -> None:
        """Attach a colorized stream handler for terminal output."""
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(colorlog.ColoredFormatter(
            "%(log_color)s[%(asctime)s] - [%(levelname)s] - %(message)s",
            datefmt=SC.DATE_FORMAT,
            log_colors=SC.LOG_COLORS
        ))
        self.addHandler(handler)

    # ------------------------------------------------------------------
    # Raw trace channel
    # ------------------------------------------------------------------

    def _write_to_file(self, text: str) -> None:
        """
        Write a raw unformatted line directly to the game trace file.

        Use this for structured sections (board grids, stat tables, headers)
        where the logging formatter's timestamps and level tags are unwanted.
        """
        with open(self._log_file, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    # ------------------------------------------------------------------
    # Abstract interface — subclasses must implement
    # ------------------------------------------------------------------

    @abstractmethod
    def _write_header(self) -> None:
        """Write the trace file header. Called once automatically on __init__."""
        ...

    @abstractmethod
    def log_move(self, player: str, move: tuple, **kwargs) -> None:
        """Record a single move to both terminal and trace file."""
        ...

    @abstractmethod
    def log_board(self, game_state: dict) -> None:
        """Record the current board state to the trace file."""
        ...

    @abstractmethod
    def log_winner(self, winner: str) -> None:
        """Record the game result to both terminal and trace file."""
        ...