import random
import copy


class CSP:
    def __init__(self, variables, domains, constraints):
        self.variables = variables
        self.domains = domains
        self.constraints = constraints
        self.solution = None

    def solve(self):
        assignment = {}
        self.solution = self.backtrack(assignment)
        return self.solution

    def backtrack(self, assignment):
        if len(assignment) == len(self.variables):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            if self.is_consistent(var, value, assignment):
                assignment[var] = value
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                del assignment[var]
        return None

    def select_unassigned_variable(self, assignment):
        unassigned_vars = [var for var in self.variables if var not in assignment]
        return min(unassigned_vars, key=lambda var: len(self.domains[var]))

    def order_domain_values(self, var, assignment):
        return self.domains[var]

    def is_consistent(self, var, value, assignment):
        for constraint_var in self.constraints[var]:
            if constraint_var in assignment and assignment[constraint_var] == value:
                return False
        return True


def build_constraints(variables):
    constraints = {}
    for var in variables:
        r, c = var
        peers = []
        for i in range(9):
            if i != r:
                peers.append((i, c))
            if i != c:
                peers.append((r, i))
        sub_r, sub_c = (r // 3) * 3, (c // 3) * 3
        for i in range(sub_r, sub_r + 3):
            for j in range(sub_c, sub_c + 3):
                if (i, j) != var:
                    peers.append((i, j))
        constraints[var] = peers
    return constraints


def solve_sudoku(board):
    variables = [(i, j) for i in range(9) for j in range(9)]
    domains = {}
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                domains[(i, j)] = set(range(1, 10))
            else:
                domains[(i, j)] = {board[i][j]}
    constraints = build_constraints(variables)

    csp = CSP(variables, domains, constraints)
    solution = csp.solve()
    if solution is None:
        return None
    result = [[0] * 9 for _ in range(9)]
    for (i, j), val in solution.items():
        result[i][j] = val
    return result


def generate_complete_board():
    board = [[0] * 9 for _ in range(9)]
    variables = [(i, j) for i in range(9) for j in range(9)]
    domains = {var: set(range(1, 10)) for var in variables}
    constraints = build_constraints(variables)

    class RandomCSP(CSP):
        def order_domain_values(self, var, assignment):
            values = list(self.domains[var])
            random.shuffle(values)
            return values

    csp = RandomCSP(variables, domains, constraints)
    solution = csp.solve()
    result = [[0] * 9 for _ in range(9)]
    for (i, j), val in solution.items():
        result[i][j] = val
    return result


def is_solvable(board):
    return solve_sudoku(board) is not None


def generate_puzzle(difficulty='easy'):
    full = generate_complete_board()
    puzzle = [row[:] for row in full]

    cells = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(cells)

    if difficulty == 'easy':
        target_clues = 38
    elif difficulty == 'medium':
        target_clues = 30
    else:
        target_clues = 25

    target_empties = 81 - target_clues
    removed = 0

    for r, c in cells:
        if removed >= target_empties:
            break
        saved = puzzle[r][c]
        puzzle[r][c] = 0
        if is_solvable(puzzle):
            removed += 1
        else:
            puzzle[r][c] = saved

    return puzzle, full


def find_conflicts(board):
    conflicts = set()
    for i in range(9):
        for j in range(9):
            val = board[i][j]
            if val == 0:
                continue
            for k in range(9):
                if k != j and board[i][k] == val:
                    conflicts.add((i, j))
                    conflicts.add((i, k))
                if k != i and board[k][j] == val:
                    conflicts.add((i, j))
                    conflicts.add((k, j))
            sub_r, sub_c = (i // 3) * 3, (j // 3) * 3
            for r in range(sub_r, sub_r + 3):
                for c in range(sub_c, sub_c + 3):
                    if (r, c) != (i, j) and board[r][c] == val:
                        conflicts.add((i, j))
                        conflicts.add((r, c))
    return list(conflicts)


def is_complete(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return False
    return len(find_conflicts(board)) == 0
