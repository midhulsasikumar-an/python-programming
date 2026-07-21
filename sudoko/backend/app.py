from flask import Flask, jsonify, request
from flask_cors import CORS
from solver import generate_puzzle, solve_sudoku, find_conflicts, is_complete

app = Flask(__name__)
CORS(app)


def board_from_request(data):
    return data.get('board')


@app.route('/api/new-game', methods=['GET'])
def new_game():
    difficulty = request.args.get('difficulty', 'easy')
    if difficulty not in ('easy', 'medium', 'hard'):
        difficulty = 'easy'
    puzzle, solution = generate_puzzle(difficulty)
    return jsonify({
        'puzzle': puzzle,
        'solution': solution,
        'difficulty': difficulty
    })


@app.route('/api/solve', methods=['POST'])
def solve():
    data = request.get_json()
    board = data.get('board')
    if not board:
        return jsonify({'error': 'No board provided'}), 400
    solution = solve_sudoku(board)
    if solution is None:
        return jsonify({'solved': False, 'solution': None})
    return jsonify({'solved': True, 'solution': solution})


@app.route('/api/validate', methods=['POST'])
def validate():
    data = request.get_json()
    board = data.get('board')
    if not board:
        return jsonify({'error': 'No board provided'}), 400
    conflicts = find_conflicts(board)
    complete = is_complete(board)
    return jsonify({
        'valid': len(conflicts) == 0,
        'conflicts': conflicts,
        'complete': complete
    })


@app.route('/api/check-completion', methods=['POST'])
def check_completion():
    data = request.get_json()
    board = data.get('board')
    if not board:
        return jsonify({'error': 'No board provided'}), 400
    complete = is_complete(board)
    return jsonify({'complete': complete})


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )
