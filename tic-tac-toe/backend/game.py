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
    return all(cell != '_' for row in b for cell in row)


def get_available_moves(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] == '_']


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
        self.scores = {'x': 0, 'o': 0, 'draw': 0}
        self.mode = 'pvp'
        self.reset()

    def reset(self):
        self.board = [['_', '_', '_'] for _ in range(3)]
        self.current_player = 'x'
        self.game_over = False
        self.move_count = 0
        self.winning_cells = []
        self.winner = None
        self.draw = False

    def make_move(self, row, col):
        if self.game_over or self.board[row][col] != '_':
            return False

        self.board[row][col] = self.current_player
        self.move_count += 1

        result = evaluate(self.board)

        if result == 10:
            self.game_over = True
            self.winner = 'x'
            self.scores['x'] += 1
            self.winning_cells = get_winning_cells(self.board)
        elif result == -10:
            self.game_over = True
            self.winner = 'o'
            self.scores['o'] += 1
            self.winning_cells = get_winning_cells(self.board)
        elif is_board_full(self.board):
            self.game_over = True
            self.draw = True
            self.scores['draw'] += 1
        else:
            self.current_player = 'o' if self.current_player == 'x' else 'x'

        return True

    def make_computer_move(self):
        if self.game_over:
            return False
        if self.mode != 'pvc':
            return False
        if self.current_player != 'o':
            return False

        move = get_best_move(self.board, 'o')
        if move is None:
            return False

        row, col = move
        return self.make_move(row, col)

    def to_dict(self):
        return {
            'board': self.board,
            'currentPlayer': self.current_player,
            'gameOver': self.game_over,
            'moveCount': self.move_count,
            'winningCells': self.winning_cells,
            'winner': self.winner,
            'draw': self.draw,
            'scores': self.scores,
            'mode': self.mode
        }
