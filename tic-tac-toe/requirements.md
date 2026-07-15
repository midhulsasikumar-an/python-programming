# Tic Tac Toe Project Requirements

## Project Goal

Create a simple Tic-Tac-Toe game in Python where two human players play against each other using a graphical interface.

The project should reuse the `evaluate()` function from the provided Google Colab notebook for winner detection.

---

## UI

Use **Tkinter** to build the graphical interface.

The UI should include:

- 3 × 3 grid of buttons
- Title: "Tic Tac Toe"
- Current player's turn (Player X / Player O)
- Restart Game button
- Winner or Draw message when the game ends

Keep the design simple, clean, and easy to understand.

---

## Game Rules

- Two players:
  - Player X
  - Player O
- Player X starts first.
- Players take turns clicking empty cells.
- A cell cannot be clicked twice.
- After every move, check whether someone has won.
- If all cells are filled and nobody wins, declare a draw.

---

## Existing Logic

The provided notebook contains an `evaluate(board)` function.

Reuse this function to determine whether:

- Player X wins
- Player O wins
- No winner yet

Do not rewrite the winner-checking logic unless necessary.

---

## Additional Logic Needed

Implement the following:

- Create the game board
- Handle button clicks
- Switch turns between players
- Detect draw condition
- Disable the board after the game ends
- Restart the game

---

## Board Representation

Use a 3 × 3 Python list to store the board.

Example:

board = [
    ["_", "_", "_"],
    ["_", "_", "_"],
    ["_", "_", "_"]
]

Update this board whenever a player clicks a cell.

---

## Game Flow

Start Game

↓

Player X clicks

↓

Update board

↓

Call evaluate(board)

↓

If winner:
    Show winner
Else if board full:
    Show draw
Else:
    Switch player

Repeat until the game finishes.

---

## UI Enhancement Requirements

The current UI is too basic. Improve it into a modern, visually appealing, and engaging desktop application while keeping the game simple and easy to use.

## Design Goal

Create a polished game interface that encourages players to keep playing. The UI should feel like a small modern desktop game rather than a basic Tkinter project.

## Theme

- Use a dark theme with accent colors.
- Choose a modern color palette (dark gray/black background with blue, cyan, green, or orange highlights).
- Use clean fonts with larger text for headings and buttons.
- Keep spacing and alignment consistent.

## Window

- Fixed window size.
- Center the window on launch.
- Add a custom window title.
- Add a simple game icon if possible.

## Board

- Large 3×3 game board.
- Square buttons with rounded appearance if possible.
- Large X and O symbols.
- Add padding between cells.
- Buttons should visually react when hovered or clicked.
- Disable occupied cells.

## Player Information

Display:

Current Turn:
Player X

or

Current Turn:
Player O

The current player's turn should be highlighted with a different color.

## Status Messages

Display clear messages such as:

- Player X Wins!
- Player O Wins!
- Match Draw!
- New Game Started

Use colors to differentiate:

- Green for winner
- Yellow for draw
- Blue for current turn

## Winning Effect

When a player wins:

- Highlight the three winning cells.
- Disable the remaining board.
- Display a congratulatory message.
- Optionally play a short system beep.

## Restart

Add a large Restart Game button.

When clicked:

- Clear the board.
- Reset the turn to Player X.
- Remove all highlights.
- Reset the status label.

## Optional Features (if easy to implement)

- Display a move counter.
- Display total wins for Player X.
- Display total wins for Player O.
- Display total draws.
- Keep the scoreboard after restarting a match.
- Add a confirmation dialog before exiting.
- Add a simple About menu.

## Animations

If possible using Tkinter:

- Smooth button hover effects.
- Brief color flash when a move is made.
- Highlight winning cells with a different background color.

Do not overcomplicate the animations.

## Code Requirements

- Keep the code modular and readable.
- Separate UI logic from game logic where practical.
- Reuse the existing evaluate(board) function from the provided notebook.
- Do not modify the winner evaluation logic unless absolutely necessary.

The application should look professional while remaining lightweight and beginner-friendly.

## Code Quality

- Keep the code simple and well organized.
- Add comments where necessary.
- Use meaningful variable and function names.
- Keep everything beginner-friendly.