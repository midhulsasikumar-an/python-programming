import random
import time


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


def minimax_limited(board, depth, is_maximizing, max_depth=2):
    result = evaluate(board)
    if result == 10:
        return 10 - depth
    if result == -10:
        return -10 + depth
    if not get_available_moves(board):
        return 0
    if depth >= max_depth:
        return evaluate(board)

    if is_maximizing:
        best = -float('inf')
        for r, c in get_available_moves(board):
            board[r][c] = 'x'
            val = minimax_limited(board, depth + 1, False, max_depth)
            board[r][c] = '_'
            best = max(best, val)
        return best
    else:
        best = float('inf')
        for r, c in get_available_moves(board):
            board[r][c] = 'o'
            val = minimax_limited(board, depth + 1, True, max_depth)
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


def get_best_move_medium(board, player):
    best_score = None
    best_move = None

    for r, c in get_available_moves(board):
        board[r][c] = player
        next_is_maximizing = (player != 'x')
        score = minimax_limited(board, 0, next_is_maximizing, max_depth=2)
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


def get_best_move_easy(board, player):
    moves = get_available_moves(board)
    if not moves:
        return None
    if random.random() < 0.7:
        return random.choice(moves)
    return get_best_move(board, player)


def get_move_quality(board, row, col, player):
    best_move = get_best_move(board, player)
    if best_move is None:
        return 'good'

    if (row, col) == best_move:
        return 'excellent'

    board_copy = [r[:] for r in board]
    board_copy[row][col] = player
    opponent = 'o' if player == 'x' else 'x'
    is_maximizing = (opponent == 'x')
    player_score = minimax(board_copy, 0, is_maximizing)

    best_board = [r[:] for r in board]
    best_board[best_move[0]][best_move[1]] = player
    best_score = minimax(best_board, 0, is_maximizing)

    if player == 'x':
        diff = best_score - player_score
    else:
        diff = player_score - best_score

    if diff <= 2:
        return 'good'
    return 'mistake'


class TicTacToeGame:
    def __init__(self, difficulty='hard'):
        self.scores = {'x': 0, 'o': 0, 'draw': 0}
        self.mode = 'pvp'
        self.difficulty = difficulty
        self.games_played = 0
        self.move_times = {'x': [], 'o': []}
        self.qualities = []
        self.all_qualities = []
        self.current_turn_start = None
        self.last_move_time = 0
        self.reset()

    def reset(self, keep_stats=False):
        self.board = [['_', '_', '_'] for _ in range(3)]
        self.current_player = 'x'
        self.game_over = False
        self.move_count = 0
        self.winning_cells = []
        self.winner = None
        self.draw = False
        self.qualities = []
        self.current_turn_start = time.time()
        self.last_move_time = 0

        if not keep_stats:
            self.games_played = 0
            self.move_times = {'x': [], 'o': []}
            self.all_qualities = []

    def get_average_move_time(self):
        all_times = self.move_times.get('x', []) + self.move_times.get('o', [])
        if not all_times:
            return None
        return round(sum(all_times) / len(all_times), 1)

    def get_win_rate(self):
        if self.games_played == 0:
            return 0
        weighted = self.scores['x'] + self.scores['draw'] * 0.5
        return round(weighted / self.games_played, 2)

    def get_skill_badge(self):
        if self.games_played < 2:
            return 'beginner'

        win_rate = self.get_win_rate()
        avg_time = self.get_average_move_time()

        if self.all_qualities:
            excellent_ratio = sum(1 for q in self.all_qualities if q == 'excellent') / len(self.all_qualities)
        else:
            excellent_ratio = 0

        score = 0
        if win_rate > 0.4:
            score += 1
        if win_rate > 0.6:
            score += 1
        if avg_time is not None and avg_time < 8:
            score += 1
        if avg_time is not None and avg_time < 4:
            score += 1
        if excellent_ratio > 0.2:
            score += 1
        if excellent_ratio > 0.5:
            score += 1

        if score >= 5:
            return 'advanced'
        elif score >= 3:
            return 'intermediate'
        return 'beginner'

    def get_coach_message(self):
        if not self.game_over:
            return None

        if self.mode == 'pvc':
            return self._coach_message_pvc()
        return self._coach_message_pvp()

    def _coach_message_pvc(self):
        if not self.qualities:
            return "Good game!"

        excellent = sum(1 for q in self.qualities if q == 'excellent')
        mistakes = sum(1 for q in self.qualities if q == 'mistake')
        center_controlled = self.board[1][1] == 'x'

        if self.winner == 'x':
            if mistakes == 0:
                return "Perfect play! Excellent game!"
            elif excellent > mistakes:
                return "Great game! You played very well."
            else:
                return "Good win! Try to reduce mistakes."
        elif self.draw:
            if excellent >= max(mistakes, 1):
                return "Great defense! You held on well."
            return "Try to be more aggressive in attack."
        else:
            if center_controlled:
                return "Good center control. Watch for tactical threats."
            return "Try controlling the center for better position."

    def _coach_message_pvp(self):
        if self.winner == 'x':
            return "Player X showed strong positional play!"
        elif self.winner == 'o':
            return "Player O made a great comeback!"
        return "Well-matched game! Both played well."

    def make_move(self, row, col):
        if self.game_over or self.board[row][col] != '_':
            return False

        now = time.time()
        if self.current_turn_start is not None:
            elapsed = now - self.current_turn_start
            self.move_times[self.current_player].append(elapsed)
            self.last_move_time = elapsed

        board_before = [r[:] for r in self.board]
        self.board[row][col] = self.current_player
        self.move_count += 1

        analyze_player = not (self.mode == 'pvc' and self.current_player == 'o')
        if analyze_player:
            quality = get_move_quality(board_before, row, col, self.current_player)
            self.qualities.append(quality)
            self.all_qualities.append(quality)

        result = evaluate(self.board)

        if result == 10:
            self.game_over = True
            self.winner = 'x'
            self.scores['x'] += 1
            self.games_played += 1
            self.winning_cells = get_winning_cells(self.board)
        elif result == -10:
            self.game_over = True
            self.winner = 'o'
            self.scores['o'] += 1
            self.games_played += 1
            self.winning_cells = get_winning_cells(self.board)
        elif is_board_full(self.board):
            self.game_over = True
            self.draw = True
            self.scores['draw'] += 1
            self.games_played += 1
        else:
            self.current_player = 'o' if self.current_player == 'x' else 'x'

        self.current_turn_start = time.time()

        return True

    def make_computer_move(self):
        if self.game_over:
            return False
        if self.mode != 'pvc':
            return False
        if self.current_player != 'o':
            return False

        if self.difficulty == 'easy':
            move = get_best_move_easy(self.board, 'o')
        elif self.difficulty == 'medium':
            move = get_best_move_medium(self.board, 'o')
        else:
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
            'mode': self.mode,
            'difficulty': self.difficulty,
            'lastMoveTime': round(self.last_move_time, 2),
            'averageMoveTime': self.get_average_move_time(),
            'lastMoveQuality': self.qualities[-1] if self.qualities else None,
            'gamesPlayed': self.games_played,
            'winRate': self.get_win_rate(),
            'skillBadge': self.get_skill_badge(),
            'coachMessage': self.get_coach_message(),
        }
