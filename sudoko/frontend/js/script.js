const API_BASE = `${window.location.origin}/api`;

let state = {
    board: [],
    initialBoard: [],
    solution: [],
    difficulty: 'easy',
    selectedCell: null,
    mistakes: 0,
    timer: 0,
    timerInterval: null,
    solved: false,
    revealed: false,
};

const boardEl = document.getElementById('board');
const numpadEl = document.getElementById('numpad');
const statusMsg = document.getElementById('status-message');
const timerEl = document.getElementById('timer-value');
const mistakesEl = document.getElementById('mistakes-value');
const loadingOverlay = document.getElementById('loading-overlay');
const completionModal = document.getElementById('completion-modal');
const completionTime = document.getElementById('completion-time');

async function api(path, options = {}) {
    const url = `${API_BASE}${path}`;
    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
}

async function newGame(difficulty) {
    stopTimer();
    state.selectedCell = null;
    state.mistakes = 0;
    state.timer = 0;
    state.solved = false;
    state.revealed = false;
    mistakesEl.textContent = '0';
    timerEl.textContent = '00:00';
    statusMsg.textContent = 'Generating puzzle...';
    completionModal.classList.add('hidden');

    showLoading(true);
    try {
        const data = await api(`/new-game?difficulty=${difficulty}`);
        state.board = data.puzzle.map(row => [...row]);
        state.initialBoard = data.puzzle.map(row => [...row]);
        state.solution = data.solution;
        state.difficulty = data.difficulty;
        state.solved = false;
        statusMsg.textContent = 'Good luck!';
        renderBoard();
        startTimer();
    } catch (e) {
        statusMsg.textContent = 'Error loading puzzle';
        console.error(e);
    } finally {
        showLoading(false);
    }
}

function renderBoard() {
    boardEl.innerHTML = '';
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = i;
            cell.dataset.col = j;

            const val = state.board[i][j];
            if (val !== 0) {
                cell.textContent = val;
                if (state.initialBoard[i][j] !== 0) {
                    cell.classList.add('given');
                } else {
                    cell.classList.add('user');
                }
            }

            cell.addEventListener('click', () => selectCell(i, j));
            boardEl.appendChild(cell);
        }
    }
    updateCellStyles();
}

function getCellEl(row, col) {
    return boardEl.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
}

function selectCell(row, col) {
    if (state.revealed) return;

    if (state.selectedCell) {
        const [pr, pc] = state.selectedCell;
        getCellEl(pr, pc)?.classList.remove('selected');
    }
    state.selectedCell = [row, col];
    const el = getCellEl(row, col);
    if (el) el.classList.add('selected');
    updateCellStyles();
}

function updateCellStyles() {
    const selected = state.selectedCell;
    const selectedVal = selected ? state.board[selected[0]][selected[1]] : 0;

    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            const el = getCellEl(i, j);
            if (!el) continue;

            el.classList.remove('highlighted-row', 'highlighted-col', 'highlighted-box', 'same-number');

            if (selected) {
                const [sr, sc] = selected;
                if (i === sr) el.classList.add('highlighted-row');
                if (j === sc) el.classList.add('highlighted-col');
                const boxR = Math.floor(sr / 3) * 3;
                const boxC = Math.floor(sc / 3) * 3;
                if (i >= boxR && i < boxR + 3 && j >= boxC && j < boxC + 3) {
                    el.classList.add('highlighted-box');
                }
                if (selectedVal !== 0 && state.board[i][j] === selectedVal && !(i === sr && j === sc)) {
                    el.classList.add('same-number');
                }
            }
        }
    }
}

async function placeNumber(num) {
    if (!state.selectedCell || state.revealed) return;
    const [row, col] = state.selectedCell;

    if (state.initialBoard[row][col] !== 0) return;

    const el = getCellEl(row, col);
    el.classList.remove('conflict');

    if (num === 0) {
        state.board[row][col] = 0;
        el.textContent = '';
        el.classList.remove('user', 'conflict');
        renderBoard();
        selectCell(row, col);
        return;
    }

    if (num < 1 || num > 9) return;

    state.board[row][col] = num;
    el.textContent = num;
    el.classList.add('user');

    if (num !== state.solution[row][col]) {
        state.mistakes++;
        mistakesEl.textContent = state.mistakes;
        el.classList.add('conflict');
        setTimeout(() => el.classList.remove('conflict'), 600);
    }

    updateCellStyles();

    if (await checkCompletion()) {
        stopTimer();
        showCompletionModal();
    }
}

async function checkCompletion() {
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            if (state.board[i][j] === 0) return false;
        }
    }
    try {
        const data = await api('/validate', {
            method: 'POST',
            body: JSON.stringify({ board: state.board }),
        });
        return data.complete;
    } catch {
        return false;
    }
}

function showCompletionModal() {
    const mins = String(Math.floor(state.timer / 60)).padStart(2, '0');
    const secs = String(state.timer % 60).padStart(2, '0');
    completionTime.textContent = `Time: ${mins}:${secs}  |  Mistakes: ${state.mistakes}`;
    completionModal.classList.remove('hidden');
}

async function checkPuzzle() {
    if (state.revealed) return;
    showLoading(true);
    try {
        const data = await api('/validate', {
            method: 'POST',
            body: JSON.stringify({ board: state.board }),
        });

        for (const cell of document.querySelectorAll('.cell')) {
            cell.classList.remove('conflict');
        }

        if (data.valid) {
            statusMsg.textContent = 'No conflicts found!';
        } else {
            statusMsg.textContent = `${data.conflicts.length} conflict(s) found`;
            for (const [r, c] of data.conflicts) {
                const el = getCellEl(r, c);
                if (el) el.classList.add('conflict');
            }
        }

        if (data.complete) {
            stopTimer();
            showCompletionModal();
        }
    } catch (e) {
        statusMsg.textContent = 'Error checking puzzle';
    } finally {
        showLoading(false);
    }
}

async function solvePuzzle() {
    if (state.revealed) return;
    showLoading(true);
    try {
        const data = await api('/solve', {
            method: 'POST',
            body: JSON.stringify({ board: state.board }),
        });

        if (!data.solved) {
            statusMsg.textContent = 'No solution exists';
            return;
        }

        state.revealed = true;
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                if (state.initialBoard[i][j] === 0) {
                    state.board[i][j] = data.solution[i][j];
                }
            }
        }
        renderBoard();
        stopTimer();
        statusMsg.textContent = 'Puzzle solved!';
    } catch (e) {
        statusMsg.textContent = 'Error solving puzzle';
    } finally {
        showLoading(false);
    }
}

function resetPuzzle() {
    if (state.revealed) return;
    for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
            if (state.initialBoard[i][j] === 0) {
                state.board[i][j] = 0;
            }
        }
    }
    state.mistakes = 0;
    mistakesEl.textContent = '0';
    renderBoard();
    statusMsg.textContent = 'Puzzle reset';
}

function showLoading(show) {
    loadingOverlay.classList.toggle('hidden', !show);
}

function startTimer() {
    stopTimer();
    state.timer = 0;
    timerEl.textContent = '00:00';
    state.timerInterval = setInterval(() => {
        state.timer++;
        const mins = String(Math.floor(state.timer / 60)).padStart(2, '0');
        const secs = String(state.timer % 60).padStart(2, '0');
        timerEl.textContent = `${mins}:${secs}`;
    }, 1000);
}

function stopTimer() {
    if (state.timerInterval) {
        clearInterval(state.timerInterval);
        state.timerInterval = null;
    }
}

document.querySelectorAll('.diff-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.diff-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        newGame(btn.dataset.difficulty);
    });
});

document.getElementById('new-game-btn').addEventListener('click', () => {
    newGame(state.difficulty);
});

document.getElementById('check-btn').addEventListener('click', checkPuzzle);
document.getElementById('solve-btn').addEventListener('click', solvePuzzle);
document.getElementById('reset-btn').addEventListener('click', resetPuzzle);
document.getElementById('modal-new-game').addEventListener('click', () => {
    completionModal.classList.add('hidden');
    newGame(state.difficulty);
});

numpadEl.addEventListener('click', e => {
    const btn = e.target.closest('.num-btn');
    if (!btn) return;
    placeNumber(parseInt(btn.dataset.value));
});

document.addEventListener('keydown', e => {
    if (e.key >= '1' && e.key <= '9') {
        placeNumber(parseInt(e.key));
    } else if (e.key === 'Backspace' || e.key === 'Delete' || e.key === '0') {
        placeNumber(0);
    } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown' || e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        e.preventDefault();
        if (!state.selectedCell) return;
        let [r, c] = state.selectedCell;
        if (e.key === 'ArrowUp') r = Math.max(0, r - 1);
        if (e.key === 'ArrowDown') r = Math.min(8, r + 1);
        if (e.key === 'ArrowLeft') c = Math.max(0, c - 1);
        if (e.key === 'ArrowRight') c = Math.min(8, c + 1);
        selectCell(r, c);
    }
});

newGame('easy');
