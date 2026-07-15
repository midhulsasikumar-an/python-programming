const API_BASE_URL = (function () {
    if (
        window.location.protocol === 'file:' ||
        window.location.hostname === '127.0.0.1' ||
        window.location.hostname === 'localhost'
    ) {
        return 'http://127.0.0.1:5000';
    }
    return 'https://your-backend.onrender.com';
})();

const state = {
    gameId: null,
    board: null,
    currentPlayer: 'x',
    gameOver: false,
    moveCount: 0,
    winningCells: [],
    winner: null,
    draw: false,
    scores: { x: 0, o: 0, draw: 0 },
    mode: 'pvp',
    isProcessing: false
};

const elements = {
    board: document.getElementById('board'),
    cells: document.querySelectorAll('.cell'),
    statusMessage: document.getElementById('status-message'),
    moveCounter: document.getElementById('move-counter'),
    scoreX: document.getElementById('score-x'),
    scoreO: document.getElementById('score-o'),
    scoreDraw: document.getElementById('score-draw'),
    restartBtn: document.getElementById('restart-btn'),
    resetScoresBtn: document.getElementById('reset-scores-btn'),
    modePvp: document.getElementById('mode-pvp'),
    modePvc: document.getElementById('mode-pvc'),
    loadingOverlay: document.getElementById('loading-overlay')
};

function apiUrl(path) {
    return API_BASE_URL + path;
}

async function createNewGame() {
    try {
        const res = await fetch(apiUrl('/api/new-game'));
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return await res.json();
    } catch (err) {
        console.error('Failed to create game:', err);
        showError('Failed to start game');
        return null;
    }
}

async function sendMove(row, col) {
    if (!state.gameId) {
        var game = await createNewGame();
        if (!game) return null;
        state.gameId = game.gameId;
    }
    try {
        var body = JSON.stringify({ gameId: state.gameId, row: row, col: col });
        var res = await fetch(apiUrl('/api/move'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: body
        });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return await res.json();
    } catch (err) {
        console.error('Failed to send move:', err);
        showError('Failed to send move');
        return null;
    }
}

async function ensureGameId() {
    if (!state.gameId) {
        var game = await createNewGame();
        if (game) {
            updateUI(game);
        }
    }
    return state.gameId;
}

async function sendRestart() {
    await ensureGameId();
    try {
        var body = JSON.stringify({ gameId: state.gameId });
        var res = await fetch(apiUrl('/api/restart'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: body
        });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return await res.json();
    } catch (err) {
        console.error('Failed to restart:', err);
        showError('Failed to restart game');
        return null;
    }
}

async function sendResetScores() {
    await ensureGameId();
    try {
        var body = JSON.stringify({ gameId: state.gameId });
        var res = await fetch(apiUrl('/api/reset-scores'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: body
        });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return await res.json();
    } catch (err) {
        console.error('Failed to reset scores:', err);
        showError('Failed to reset scores');
        return null;
    }
}

async function sendSetMode(mode) {
    await ensureGameId();
    try {
        var body = JSON.stringify({ gameId: state.gameId, mode: mode });
        var res = await fetch(apiUrl('/api/mode'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: body
        });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return await res.json();
    } catch (err) {
        console.error('Failed to set mode:', err);
        showError('Failed to switch mode');
        return null;
    }
}

function showError(message) {
    const msg = elements.statusMessage;
    msg.className = 'status-message';
    msg.textContent = message;
    msg.style.color = '#e74c3c';
    setTimeout(() => {
        if (msg.textContent === message) {
            msg.style.color = '';
            renderStatus();
        }
    }, 3000);
}

function updateUI(data) {
    state.gameId = data.gameId;
    state.board = data.board;
    state.currentPlayer = data.currentPlayer;
    state.gameOver = data.gameOver;
    state.moveCount = data.moveCount;
    state.winningCells = data.winningCells;
    state.winner = data.winner;
    state.draw = data.draw;
    state.scores = data.scores;
    state.mode = data.mode;

    renderBoard();
    renderStatus();
    renderScoreboard();
    renderModeButtons();
}

function renderBoard() {
    elements.cells.forEach((cell, index) => {
        const row = Math.floor(index / 3);
        const col = index % 3;
        const value = state.board[row][col];
        const isWinning = state.winningCells.some(function (pair) {
            return pair[0] === row && pair[1] === col;
        });

        cell.innerHTML = '';
        cell.className = 'cell';

        if (value !== '_') {
            cell.classList.add('marked');
            cell.classList.add(value === 'x' ? 'marked-x' : 'marked-o');
            const span = document.createElement('span');
            span.className = 'mark';
            span.textContent = value.toUpperCase();
            cell.appendChild(span);
        }

        if (state.gameOver) {
            cell.classList.add('disabled');
            if (isWinning) {
                cell.classList.add('winning');
            }
        } else if (value !== '_') {
            cell.classList.add('disabled');
        }
    });
}

function renderStatus() {
    const msg = elements.statusMessage;
    msg.className = 'status-message';
    msg.style.color = '';

    if (state.gameOver) {
        if (state.winner) {
            var label = state.mode === 'pvc' && state.winner === 'o' ? 'Computer' : 'Player ' + state.winner.toUpperCase();
            msg.textContent = label + ' Wins!';
            msg.classList.add('win');
        } else if (state.draw) {
            msg.textContent = 'Match Draw!';
            msg.classList.add('draw');
        }
    } else {
        if (state.mode === 'pvc' && state.currentPlayer === 'o') {
            msg.textContent = "Computer's Turn";
            msg.classList.add('computer');
        } else {
            var label = state.mode === 'pvc' && state.currentPlayer === 'x' ? 'You (X)' : 'Player ' + state.currentPlayer.toUpperCase();
            msg.textContent = label + "'s Turn";
            msg.classList.add(state.currentPlayer === 'x' ? 'turn-x' : 'turn-o');
        }
    }

    elements.moveCounter.textContent = 'Moves: ' + state.moveCount;
}

function renderScoreboard() {
    elements.scoreX.textContent = state.scores.x;
    elements.scoreO.textContent = state.scores.o;
    elements.scoreDraw.textContent = state.scores.draw;
}

function renderModeButtons() {
    elements.modePvp.classList.toggle('active', state.mode === 'pvp');
    elements.modePvc.classList.toggle('active', state.mode === 'pvc');
}

function setLoading(loading) {
    if (loading) {
        elements.loadingOverlay.classList.remove('hidden');
    } else {
        elements.loadingOverlay.classList.add('hidden');
    }
}

async function handleCellClick(e) {
    if (state.isProcessing) return;

    var cell = e.currentTarget;

    if (state.gameOver) return;
    if (state.mode === 'pvc' && state.currentPlayer === 'o') return;

    var row = parseInt(cell.dataset.row, 10);
    var col = parseInt(cell.dataset.col, 10);

    if (state.board[row][col] !== '_') return;

    state.isProcessing = true;

    if (state.mode === 'pvc') {
        setLoading(true);
    }

    var data = await sendMove(row, col);
    state.isProcessing = false;

    if (state.mode === 'pvc') {
        setLoading(false);
    }

    if (data && !data.error) {
        updateUI(data);
    }
}

async function handleRestart() {
    var data = await sendRestart();
    if (data) {
        updateUI(data);
    }
}

async function handleResetScores() {
    var data = await sendResetScores();
    if (data) {
        updateUI(data);
    }
}

async function handleModeChange(e) {
    var btn = e.currentTarget;
    var mode = btn.dataset.mode;

    if (mode === state.mode) return;

    var data = await sendSetMode(mode);
    if (data) {
        updateUI(data);
    }
}

function init() {
    elements.cells.forEach(function (cell) {
        cell.addEventListener('click', handleCellClick);
    });

    elements.restartBtn.addEventListener('click', handleRestart);
    elements.resetScoresBtn.addEventListener('click', handleResetScores);
    elements.modePvp.addEventListener('click', handleModeChange);
    elements.modePvc.addEventListener('click', handleModeChange);

    createNewGame().then(function (data) {
        if (data) {
            updateUI(data);
        }
    });
}

document.addEventListener('DOMContentLoaded', init);
