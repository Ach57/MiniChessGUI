# Game controller — architecture

## Overview

The diagram represents a controller hierarchy for a game system that supports multiple play modes:

- Player vs Player (PvP)
- Player vs AI (PvAI)
- AI vs AI

At the core is a shared base class, **`GameController`**, which provides common functionality, while specialized controllers extend it to implement specific behaviors.

---

### Base Class: GameController

`GameController` is the abstract foundation for all game modes.

**Responsibilities**

- Holds references to:
  - the game engine (game state & rules)
  - the view (UI layer)

- Implements shared logic:
  - \_apply_and_refresh() → applies a move and updates the UI
  - \_check_winner() → determines if the game is over

- Declares an abstract method:
  - start() → defines how each game mode begins

This design centralizes all common game logic, avoiding duplication across modes.

---

### PvPController (Player vs Player)

This controller handles human vs human interaction.

**Adds:**

- \_handle_select() → processes selecting a piece/square
- \_handle_move() → processes a move attempt

**Behavior:**

- Connects to user interactions from the view:
  - on_square_selected
  - on_move_attempted

Both players are humans, so all actions come from UI events.

---

### PvAIController (Player vs AI)

This controller manages a hybrid interaction between a human and an AI.

**Adds:**

- \_handle_select() → human selects a piece
- \_handle_move() → human makes a move
- \_handle_ai_turn() → AI computes and plays its move

**Behavior:**

- Wires the same human events as PvP:
  - on_square_selected
  - on_move_attempted

- Additionally listens for:
  - on_ai_turn_requested

After a human move, the AI takes over automatically when triggered.

---

### AiVsAiController (AI vs AI)

This controller handles a fully automated game.

**Adds:**

- \_handle_ai_turn() → executes moves for both sides

**Overrides:**

- start() → immediately begins an automated loop

**Behavior:**

- No interaction with the view
- No user input
- Runs a continuous loop where both players are AI

This mode is useful for simulations, testing, or demonstrations.

---

### UML diagram:

```mermaid
classDiagram
    class GameController {
        <<abstract>>
        # engine: GameEngine
        # view: BaseChessGUI
        + start()*
        # _apply_and_refresh(move) bool
        # _check_winner() str
    }

    class PvPController {
        + start()
        # _handle_select(x, y)
        # _handle_move(origin, destination)
    }

    class PvAIController {
        + start()
        # _handle_select(x, y)
        # _handle_move(origin, destination)
        # _handle_ai_turn()
    }

    class AiVsAiController {
        + start()
        # _handle_ai_turn()
    }

    class GameEngine {
        + state dict
        + is_valid_move(move) bool
        + apply_move(move)
        + is_game_over() str
        + valid_moves() list
    }

    class BaseChessGUI {
        <<abstract>>
        + on_square_selected(x, y)
        + on_move_attempted(origin, destination)
        + on_ai_turn_requested()
        + highlight_square(x, y)
        + deselect_square(x, y)
        + update_board(message)
        + disable_buttons()
        + show_error(message)
        + show_warning(message)
    }

    class PlayerVsPlayerGui {
        + on_square_selected(x, y)
        + on_move_attempted(origin, destination)
    }

    class PlayerVsAiGui {
        + on_square_selected(x, y)
        + on_move_attempted(origin, destination)
        + on_ai_turn_requested()
    }

    class AiVsAiGui {
        + on_ai_turn_requested()
    }

    GameController <|-- PvPController : extends
    GameController <|-- PvAIController : extends
    GameController <|-- AiVsAiController : extends

    BaseChessGUI <|-- PlayerVsPlayerGui : extends
    BaseChessGUI <|-- PlayerVsAiGui : extends
    BaseChessGUI <|-- AiVsAiGui : extends

    GameController o-- GameEngine : owns
    GameController o-- BaseChessGUI : owns

    PvPController ..> PlayerVsPlayerGui : wires callbacks
    PvAIController ..> PlayerVsAiGui : wires callbacks
    AiVsAiController ..> AiVsAiGui : no callbacks

    note for PvPController "Wires: on_square_selected, on_move_attempted"
    note for PvAIController "Wires: on_square_selected, on_move_attempted, on_ai_turn_requested"
    note for AiVsAiController "No human callbacks. start() kicks off automated loop"
```
