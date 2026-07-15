import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, Menu
import winsound


# =============================================================================
# GAME LOGIC
# =============================================================================

def evaluate(b):
    for row in range(0, 3):
        if b[row][0] == b[row][1] and b[row][1] == b[row][2]:
            if b[row][0] == 'x':
                return 10
            elif b[row][0] == 'o':
                return -10

    for col in range(0, 3):
        if b[0][col] == b[1][col] and b[1][col] == b[2][col]:
            if b[0][col] == 'x':
                return 10
            elif b[0][col] == 'o':
                return -10

    if b[0][0] == b[1][1] and b[1][1] == b[2][2]:
        if b[0][0] == 'x':
            return 10
        elif b[0][0] == 'o':
            return -10

    if b[0][2] == b[1][1] and b[1][1] == b[2][0]:
        if b[0][2] == 'x':
            return 10
        elif b[0][2] == 'o':
            return -10

    return 0


def get_winning_cells(b):
    for row in range(3):
        if b[row][0] == b[row][1] == b[row][2] != '_':
            return [(row, 0), (row, 1), (row, 2)]
    for col in range(3):
        if b[0][col] == b[1][col] == b[2][col] != '_':
            return [(0, col), (1, col), (2, col)]
    if b[0][0] == b[1][1] == b[2][2] != '_':
        return [(0, 0), (1, 1), (2, 2)]
    if b[0][2] == b[1][1] == b[2][0] != '_':
        return [(0, 2), (1, 1), (2, 0)]
    return []


def is_board_full(b):
    return all(cell != "_" for row in b for cell in row)


def get_available_moves(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] == "_"]


def minimax(board, depth, is_maximizing):
    result = evaluate(board)
    if result == 10:
        return 10 - depth
    if result == -10:
        return -10 + depth
    if not get_available_moves(board):
        return 0

    if is_maximizing:
        best = -float('inf')
        for r, c in get_available_moves(board):
            board[r][c] = 'x'
            val = minimax(board, depth + 1, False)
            board[r][c] = '_'
            best = max(best, val)
        return best
    else:
        best = float('inf')
        for r, c in get_available_moves(board):
            board[r][c] = 'o'
            val = minimax(board, depth + 1, True)
            board[r][c] = '_'
            best = min(best, val)
        return best


def get_best_move(board, player):
    best_score = None
    best_move = None

    for r, c in get_available_moves(board):
        board[r][c] = player
        next_is_maximizing = (player != 'x')
        score = minimax(board, 0, next_is_maximizing)
        board[r][c] = '_'

        if player == 'x':
            if best_score is None or score > best_score:
                best_score = score
                best_move = (r, c)
        else:
            if best_score is None or score < best_score:
                best_score = score
                best_move = (r, c)

    return best_move


class TicTacToeGame:
    def __init__(self):
        self.scores = {"x": 0, "o": 0, "draw": 0}
        self.mode = "pvp"
        self.reset()

    def reset(self):
        self.board = [["_", "_", "_"] for _ in range(3)]
        self.current_player = "x"
        self.game_over = False
        self.move_count = 0
        self.winning_cells = []

    def make_move(self, row, col):
        if self.game_over or self.board[row][col] != "_":
            return False
        self.board[row][col] = self.current_player
        self.move_count += 1
        result = evaluate(self.board)
        if result == 10:
            self.game_over = True
            self.scores["x"] += 1
            self.winning_cells = get_winning_cells(self.board)
        elif result == -10:
            self.game_over = True
            self.scores["o"] += 1
            self.winning_cells = get_winning_cells(self.board)
        elif is_board_full(self.board):
            self.game_over = True
            self.scores["draw"] += 1
        else:
            self.current_player = "o" if self.current_player == "x" else "x"
        return True

    def is_computer_turn(self):
        return self.mode == "pvc" and self.current_player == "o" and not self.game_over


# =============================================================================
# UI
# =============================================================================

WIN_COLOR = "#2ECC71"
DRAW_COLOR = "#F1C40F"
TURN_COLOR = "#3498DB"
HIGHLIGHT_COLOR = "#27AE60"


class TicTacToeUI:
    def __init__(self):
        self.game = TicTacToeGame()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()
        self.root.title("Tic Tac Toe")
        self.center_window(420, 660)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.default_btn_color = None
        self.computer_thinking = False
        self.computer_after_id = None
        self.build_ui()
        self.update_ui()

    def center_window(self, width, height):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to exit?"):
            self.root.destroy()

    def build_ui(self):
        menubar = Menu(self.root)
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menubar)

        title = ctk.CTkLabel(
            self.root, text="Tic Tac Toe",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=(15, 2))

        mode_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        mode_frame.pack(pady=(2, 5))

        mode_label = ctk.CTkLabel(mode_frame, text="Mode:", font=("Arial", 13))
        mode_label.pack(side="left", padx=(0, 8))

        self.mode_option = ctk.CTkOptionMenu(
            mode_frame,
            values=["Human vs Human", "Human vs Computer"],
            font=("Arial", 13),
            command=self.on_mode_change
        )
        self.mode_option.pack(side="left")

        self.score_label = ctk.CTkLabel(
            self.root, text="", font=("Arial", 13)
        )
        self.score_label.pack()

        self.move_label = ctk.CTkLabel(
            self.root, text="Moves: 0", font=("Arial", 12)
        )
        self.move_label.pack(pady=(2, 0))

        self.turn_label = ctk.CTkLabel(
            self.root, text="", font=("Arial", 18, "bold")
        )
        self.turn_label.pack(pady=(12, 10))

        board_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        board_frame.pack()

        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                btn = ctk.CTkButton(
                    board_frame, text="", width=100, height=100,
                    font=("Arial", 36, "bold"),
                    corner_radius=12,
                    command=lambda r=i, c=j: self.on_click(r, c)
                )
                btn.grid(row=i, column=j, padx=4, pady=4)
                self.buttons[i][j] = btn

        self.default_btn_color = self.buttons[0][0].cget("fg_color")

        self.restart_btn = ctk.CTkButton(
            self.root, text="Restart Game",
            font=("Arial", 16, "bold"),
            height=40, corner_radius=8,
            command=self.restart
        )
        self.restart_btn.pack(pady=(15, 10))

    def on_mode_change(self, choice):
        self.game.mode = "pvc" if "Computer" in choice else "pvp"
        self.cancel_computer_move()
        self.restart()

    def cancel_computer_move(self):
        if self.computer_after_id is not None:
            self.root.after_cancel(self.computer_after_id)
            self.computer_after_id = None
        self.computer_thinking = False

    def update_ui(self):
        s = self.game.scores
        self.score_label.configure(
            text=f"Player X: {s['x']}  |  Player O: {s['o']}  |  Draws: {s['draw']}"
        )
        self.move_label.configure(text=f"Moves: {self.game.move_count}")

        if self.game.game_over:
            if self.game.winning_cells:
                winner = "X" if self.game.current_player == "x" else "O"
                self.turn_label.configure(
                    text=f"Player {winner} Wins!",
                    text_color=WIN_COLOR
                )
                self.highlight_winning_cells()
                winsound.Beep(800, 200)
            else:
                self.turn_label.configure(
                    text="Match Draw!",
                    text_color=DRAW_COLOR
                )
        else:
            player_text = self.game.current_player.upper()
            suffix = ""
            if self.game.mode == "pvc" and self.game.current_player == "o":
                suffix = " (Computer)"
            self.turn_label.configure(
                text=f"Current Turn: Player {player_text}{suffix}",
                text_color=TURN_COLOR
            )

    def highlight_winning_cells(self):
        for r, c in self.game.winning_cells:
            self.buttons[r][c].configure(fg_color=HIGHLIGHT_COLOR)

    def clear_highlights(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].configure(fg_color=self.default_btn_color)

    def disable_all_buttons(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].configure(state="disabled")

    def enable_empty_cells(self):
        for i in range(3):
            for j in range(3):
                if self.game.board[i][j] == "_":
                    self.buttons[i][j].configure(state="normal")

    def on_click(self, row, col):
        if self.game.game_over or self.computer_thinking:
            return
        if self.game.board[row][col] != "_":
            return

        self.game.make_move(row, col)
        self.buttons[row][col].configure(
            text=self.game.board[row][col].upper(),
            state="disabled"
        )

        if self.game.game_over:
            self.disable_all_buttons()

        self.update_ui()

        if self.game.is_computer_turn():
            self.computer_thinking = True
            self.disable_all_buttons()
            self.computer_after_id = self.root.after(500, self.computer_move)

    def computer_move(self):
        self.computer_after_id = None

        if not self.game.is_computer_turn():
            self.computer_thinking = False
            return

        move = get_best_move(self.game.board, "o")
        if move is None:
            self.computer_thinking = False
            return

        r, c = move
        self.game.make_move(r, c)
        self.buttons[r][c].configure(
            text=self.game.board[r][c].upper(),
            state="disabled"
        )

        self.computer_thinking = False

        if self.game.game_over:
            self.disable_all_buttons()
        else:
            self.enable_empty_cells()

        self.update_ui()

    def restart(self):
        self.cancel_computer_move()
        self.game.reset()
        self.clear_highlights()
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].configure(
                    text="", state="normal",
                    fg_color=self.default_btn_color
                )
        self.update_ui()

    def show_about(self):
        messagebox.showinfo(
            "About",
            "Tic Tac Toe\n\n"
            "A modern desktop game built with Python & CustomTkinter.\n\n"
            "Two players take turns marking spaces in a 3x3 grid.\n"
            "The first to get three in a row wins!"
        )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = TicTacToeUI()
    app.run()