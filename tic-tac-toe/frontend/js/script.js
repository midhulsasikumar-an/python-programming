const API_BASE_URL = (function () {
    if (
        window.location.protocol === 'file:' ||
        window.location.hostname === '127.0.0.1' ||
        window.location.hostname === 'localhost'
    ) {
        return 'http://127.0.0.1:5000';
    }
    return 'https://tic-tac-toe-d3sx.onrender.com';
})();

const FETCH_TIMEOUT_MS = 20000;
const RETRY_MAX = 3;

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
    difficulty: 'hard',
    isProcessing: false,
    lastMoveQuality: null,
    coachMessage: null,
    gamesPlayed: 0,
    winRate: 0,
    skillBadge: 'beginner',
    averageMoveTime: null
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
    loadingOverlay: document.getElementById('loading-overlay'),
    timerValue: document.getElementById('timer-value'),
    moveQuality: document.getElementById('move-quality'),
    coachMessage: document.getElementById('coach-message'),
    statGames: document.getElementById('stat-games'),
    statWins: document.getElementById('stat-wins'),
    statLosses: document.getElementById('stat-losses'),
    statDraws: document.getElementById('stat-draws'),
    statWinRate: document.getElementById('stat-winrate'),
    statAvgTime: document.getElementById('stat-avgtime'),
    skillBadge: document.getElementById('skill-badge'),
    diffBtns: document.querySelectorAll('.diff-btn')
};

var timerInterval = null;
var timerSeconds = 0;

function apiUrl(path) {
    return API_BASE_URL + path;
}

async function fetchWithTimeout(url, options) {
    const controller = new AbortController();
    const timer = setTimeout(function () {
        controller.abort();
    }, FETCH_TIMEOUT_MS);
    try {
        var res = await fetch(url, Object.assign({}, options, { signal: controller.signal }));
        return res;
    } finally {
        clearTimeout(timer);
    }
}

async function createNewGame() {
    for (var attempt = 1; attempt <= RETRY_MAX; attempt++) {
        try {
            var url = apiUrl('/api/new-game') + '?difficulty=' + state.difficulty;
            var res = await fetchWithTimeout(url);
            if (!res.ok) throw new Error('HTTP ' + res.status);
            return await res.json();
        } catch (err) {
            console.error('Failed to create game (attempt ' + attempt + '):', err);
            if (attempt < RETRY_MAX) {
                await new Promise(function (r) { setTimeout(r, 1000 * attempt); });
            }
        }
    }
    showError('Failed to start game. Please refresh the page.');
    return null;
}

async function sendMove(row, col) {
    if (!state.gameId) {
        var game = await createNewGame();
        if (!game) return null;
        state.gameId = game.gameId;
    }
    try {
        var body = JSON.stringify({ gameId: state.gameId, row: row, col: col });
        var res = await fetchWithTimeout(apiUrl('/api/move'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: body
        });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return await res.json();
    } catch (err) {
        console.error('Failed to send move:', err);
        showError('Failed to send move. Try again.');
        return null;
    }
}

async function ensureGameId() {
    if (!state.gameId) {
        var game = await createNewGame();
        if (game) {
            clearError();
            updateUI(game);
        }
    }
    return state.gameId;
}

async function sendRestart() {
    await ensureGameId();
    clearError();
    try {
        var body = JSON.stringify({ gameId: state.gameId });
        var res = await fetchWithTimeout(apiUrl('/api/restart'), {
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
    clearError();
    try {
        var body = JSON.stringify({ gameId: state.gameId });
        var res = await fetchWithTimeout(apiUrl('/api/reset-scores'), {
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
    clearError();
    try {
        var body = JSON.stringify({ gameId: state.gameId, mode: mode, difficulty: state.difficulty });
        var res = await fetchWithTimeout(apiUrl('/api/mode'), {
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

async function sendSetDifficulty(difficulty) {
    await ensureGameId();
    clearError();
    try {
        var body = JSON.stringify({ gameId: state.gameId, mode: state.mode, difficulty: difficulty });
        var res = await fetchWithTimeout(apiUrl('/api/mode'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: body
        });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return await res.json();
    } catch (err) {
        console.error('Failed to set difficulty:', err);
        return null;
    }
}

function showError(message) {
    const msg = elements.statusMessage;
    msg.className = 'status-message';
    msg.textContent = message;
    msg.style.color = '#e74c3c';
}

function clearError() {
    const msg = elements.statusMessage;
    msg.style.color = '';
    renderStatus();
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
    state.difficulty = data.difficulty || state.difficulty;
    state.lastMoveQuality = data.lastMoveQuality || null;
    state.gamesPlayed = data.gamesPlayed || 0;
    state.winRate = data.winRate || 0;
    state.skillBadge = data.skillBadge || 'beginner';
    state.averageMoveTime = data.averageMoveTime;

    renderBoard();
    renderStatus();
    renderScoreboard();
    renderModeButtons();
    renderDifficultyButtons();
    renderQuality();
    renderStats();
    renderSkillBadge();
    renderCoachMessage();

    resetTimer();
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

function renderDifficultyButtons() {
    elements.diffBtns.forEach(function (btn) {
        btn.classList.toggle('active', btn.dataset.difficulty === state.difficulty);
    });
}

function renderQuality() {
    const el = elements.moveQuality;
    if (state.lastMoveQuality) {
        el.textContent = state.lastMoveQuality.charAt(0).toUpperCase() + state.lastMoveQuality.slice(1);
        el.className = 'quality-display ' + state.lastMoveQuality;
    } else {
        el.textContent = '\u2014';
        el.className = 'quality-display';
    }
}

function renderStats() {
    elements.statGames.textContent = state.gamesPlayed;
    elements.statWins.textContent = state.scores.x;
    elements.statLosses.textContent = state.scores.o;
    elements.statDraws.textContent = state.scores.draw;
    elements.statWinRate.textContent = Math.round(state.winRate * 100) + '%';
    elements.statAvgTime.textContent = state.averageMoveTime !== null && state.averageMoveTime !== undefined
        ? state.averageMoveTime + 's'
        : '\u2014';
}

function renderSkillBadge() {
    const el = elements.skillBadge;
    var label = state.skillBadge.charAt(0).toUpperCase() + state.skillBadge.slice(1);
    el.textContent = label;
    el.className = 'skill-badge ' + state.skillBadge;
}

function renderCoachMessage() {
    const el = elements.coachMessage;
    if (state.coachMessage && state.gameOver) {
        el.textContent = state.coachMessage;
        el.classList.remove('hidden');
    } else {
        el.classList.add('hidden');
    }
}

function resetTimer() {
    stopTimer();
    timerSeconds = 0;
    updateTimerDisplay();
    startTimer();
}

function startTimer() {
    if (timerInterval) return;
    if (state.gameOver || (state.mode === 'pvc' && state.currentPlayer === 'o')) return;
    timerInterval = setInterval(function () {
        timerSeconds++;
        updateTimerDisplay();
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function updateTimerDisplay() {
    var mins = Math.floor(timerSeconds / 60);
    var secs = timerSeconds % 60;
    elements.timerValue.textContent =
        String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
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

    if (!state.board || !state.gameId) {
        await ensureGameId();
        if (!state.board) return;
    }

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
        clearError();
        updateUI(data);
    }
}

async function handleRestart() {
    var data = await sendRestart();
    if (data) {
        clearError();
        updateUI(data);
    }
}

async function handleResetScores() {
    var data = await sendResetScores();
    if (data) {
        clearError();
        updateUI(data);
    }
}

async function handleModeChange(e) {
    if (state.isProcessing) return;
    var btn = e.currentTarget;
    var mode = btn.dataset.mode;

    if (mode === state.mode) return;

    var data = await sendSetMode(mode);
    if (data) {
        clearError();
        updateUI(data);
    }
}

async function handleDifficultyChange(e) {
    if (state.isProcessing) return;
    var btn = e.currentTarget;
    var difficulty = btn.dataset.difficulty;

    if (difficulty === state.difficulty) return;

    var data = await sendSetDifficulty(difficulty);
    if (data) {
        clearError();
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

    elements.diffBtns.forEach(function (btn) {
        btn.addEventListener('click', handleDifficultyChange);
    });

    createNewGame().then(function (data) {
        if (data) {
            clearError();
            updateUI(data);
        }
    });
}

document.addEventListener('DOMContentLoaded', init);
