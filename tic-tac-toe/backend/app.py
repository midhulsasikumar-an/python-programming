import os
import uuid
from flask import Flask, jsonify, request
from flask_cors import CORS
from game import TicTacToeGame

app = Flask(__name__)
CORS(app)

games = {}


def get_or_create_game(game_id):
    if game_id and game_id in games:
        return games[game_id], game_id
    game = TicTacToeGame()
    new_id = str(uuid.uuid4())
    games[new_id] = game
    return game, new_id


def respond(game, game_id):
    state = game.to_dict()
    state['gameId'] = game_id
    return jsonify(state)


@app.route('/api/new-game', methods=['GET'])
def new_game():
    game = TicTacToeGame()
    game_id = str(uuid.uuid4())
    games[game_id] = game
    return respond(game, game_id)


@app.route('/api/state', methods=['GET'])
def get_state():
    game_id = request.args.get('gameId', '')
    game, gid = get_or_create_game(game_id)
    return respond(game, gid)


@app.route('/api/move', methods=['POST'])
def make_move():
    data = request.get_json()
    game_id = data.get('gameId', '')
    row = data.get('row')
    col = data.get('col')

    if row is None or col is None:
        return jsonify({'error': 'Missing row or col'}), 400

    game, gid = get_or_create_game(game_id)
    success = game.make_move(int(row), int(col))

    if not success:
        return jsonify({'error': 'Invalid move', 'state': game.to_dict()}), 400

    if not game.game_over and game.mode == 'pvc' and game.current_player == 'o':
        game.make_computer_move()

    return respond(game, gid)


@app.route('/api/mode', methods=['POST'])
def set_mode():
    data = request.get_json()
    game_id = data.get('gameId', '')
    mode = data.get('mode')

    if mode not in ('pvp', 'pvc'):
        return jsonify({'error': 'Invalid mode'}), 400

    game, gid = get_or_create_game(game_id)
    game.mode = mode
    game.reset()
    return respond(game, gid)


@app.route('/api/restart', methods=['POST'])
def restart():
    data = request.get_json()
    game_id = data.get('gameId', '')

    game, gid = get_or_create_game(game_id)
    scores = game.scores
    mode = game.mode
    game.reset()
    game.scores = scores
    game.mode = mode
    return respond(game, gid)


@app.route('/api/reset-scores', methods=['POST'])
def reset_scores():
    data = request.get_json()
    game_id = data.get('gameId', '')

    game, gid = get_or_create_game(game_id)
    mode = game.mode
    game.reset()
    game.scores = {'x': 0, 'o': 0, 'draw': 0}
    game.mode = mode
    return respond(game, gid)


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
