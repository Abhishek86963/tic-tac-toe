/**
 * ═══════════════════════════════════════════════════════════
 *  script.js  —  Tic Tac Toe Smart Game
 *  College Innovative Assignment | Web Version
 * ═══════════════════════════════════════════════════════════
 *
 *  TABLE OF CONTENTS:
 *  1.  Game State Variables
 *  2.  Win Combinations
 *  3.  Board Setup
 *  4.  Game Flow (startGame, setMode, makeMove)
 *  5.  Win & Draw Detection
 *  6.  AI Engine (Minimax Algorithm)
 *  7.  Sound Effects (Web Audio API)
 *  8.  UI Helpers (status, score, stats, popup)
 *  9.  Theme Toggle (Dark / Light)
 *  10. Initialization
 * ═══════════════════════════════════════════════════════════
 */


/* ── 1. GAME STATE VARIABLES ─────────────────────────────────
   These variables track the entire state of the game.
   Keeping all state in one place makes the code easy to
   debug and reset.                                          */

let board         = Array(9).fill('');  // 9 cells, empty string = empty
let currentPlayer = 'X';               // Who is playing right now
let gameActive    = false;             // Is the game running?
let gameMode      = 'pvp';             // 'pvp' = Player vs Player, 'pvc' = vs AI

// Score tracking
let scoreX    = 0;
let scoreO    = 0;
let scoreDraw = 0;
let totalGames = 0;

// Statistics
let fastestWin    = null;  // Minimum moves taken to win any game
let movesThisGame = 0;     // Moves made in the current game


/* ── 2. WIN COMBINATIONS ─────────────────────────────────────
   All 8 possible ways to win in Tic Tac Toe:
   - 3 rows, 3 columns, 2 diagonals                         */
const WIN_COMBOS = [
  [0, 1, 2],  // Top row
  [3, 4, 5],  // Middle row
  [6, 7, 8],  // Bottom row
  [0, 3, 6],  // Left column
  [1, 4, 7],  // Middle column
  [2, 5, 8],  // Right column
  [0, 4, 8],  // Diagonal top-left → bottom-right
  [2, 4, 6],  // Diagonal top-right → bottom-left
];


/* ── 3. BOARD SETUP ──────────────────────────────────────────
   We dynamically create the 9 cells using JavaScript
   instead of hardcoding them in HTML.
   This is cleaner and allows easy reset.                   */

/**
 * buildBoard()
 * Creates 9 cell <div> elements and appends them to #board.
 * Each cell gets a data-idx attribute so we know which cell
 * was clicked.
 */
function buildBoard() {
  const boardEl = document.getElementById('board');
  boardEl.innerHTML = ''; // Clear existing cells

  for (let i = 0; i < 9; i++) {
    const cell = document.createElement('div');
    cell.className = 'cell';
    cell.dataset.idx = i;
    cell.addEventListener('click', () => onCellClick(i));
    boardEl.appendChild(cell);
  }
}

/**
 * getCell(idx)
 * Helper: returns the DOM element for a cell by index.
 */
function getCell(idx) {
  return document.querySelector(`.cell[data-idx="${idx}"]`);
}


/* ── 4. GAME FLOW ─────────────────────────────────────────────*/

/**
 * startGame()
 * Resets the board for a new game without clearing scores.
 * Called at startup, on Restart button, and after popup closes.
 */
function startGame() {
  board         = Array(9).fill('');
  currentPlayer = 'X';
  gameActive    = true;
  movesThisGame = 0;

  // Visually reset every cell
  for (let i = 0; i < 9; i++) {
    const cell = getCell(i);
    cell.className = 'cell';  // Remove 'taken', 'winner', etc.
    cell.innerHTML = '';       // Remove symbol
  }

  updateStatus();
  updateStats();
}

/**
 * setMode(mode)
 * Switch between 'pvp' and 'pvc' game modes.
 * Also resets scores since it's a new kind of game.
 */
function setMode(mode) {
  gameMode = mode;

  // Update button active state
  document.getElementById('btn-pvp').classList.toggle('active', mode === 'pvp');
  document.getElementById('btn-pvc').classList.toggle('active', mode === 'pvc');

  resetScore();   // Fresh start for new mode
  startGame();
}

/**
 * onCellClick(idx)
 * Called when a player clicks a cell.
 * Validates the click before passing to makeMove().
 */
function onCellClick(idx) {
  if (!gameActive)          return;  // Game is over
  if (board[idx] !== '')    return;  // Cell is already taken
  if (gameMode === 'pvc' && currentPlayer === 'O') return;  // AI's turn, block click

  makeMove(idx, currentPlayer);
}

/**
 * makeMove(idx, player)
 * CORE FUNCTION — applies a move to the board.
 *
 * Steps:
 * 1. Update the board array
 * 2. Render the symbol with animation
 * 3. Check for win or draw
 * 4. Switch player or trigger AI
 */
function makeMove(idx, player) {
  // 1. Update internal board state
  board[idx] = player;
  movesThisGame++;

  // 2. Render symbol on the cell
  const cell = getCell(idx);
  cell.classList.add('taken');
  const symbol = player === 'X' ? '✕' : '○';
  cell.innerHTML = `<span class="sym ${player.toLowerCase()}">${symbol}</span>`;

  // Ripple click animation
  cell.classList.add('ripple');
  setTimeout(() => cell.classList.remove('ripple'), 450);

  // Play a click sound
  playSound(player === 'X' ? 'click_x' : 'click_o');

  // 3. Check results
  const winCombo = getWinnerCombo();
  if (winCombo) {
    handleWin(player, winCombo);
    return;
  }
  if (board.every(cell => cell !== '')) {
    handleDraw();
    return;
  }

  // 4. Switch player
  currentPlayer = (player === 'X') ? 'O' : 'X';
  updateStatus();
  updateStats();

  // If PvC mode and it's now AI's turn
  if (gameMode === 'pvc' && currentPlayer === 'O' && gameActive) {
    gameActive = false;  // Lock board so player can't click during AI thinking
    setTimeout(() => {
      gameActive = true;
      const aiIdx = bestMove([...board]);  // Ask AI for best move
      makeMove(aiIdx, 'O');
    }, 450);
  }
}


/* ── 5. WIN & DRAW DETECTION ─────────────────────────────────*/

/**
 * getWinnerCombo()
 * Checks all 8 win combinations.
 * Returns the winning combo array [a,b,c] or null.
 */
function getWinnerCombo() {
  for (const combo of WIN_COMBOS) {
    const [a, b, c] = combo;
    if (board[a] && board[a] === board[b] && board[b] === board[c]) {
      return combo;  // Found a winner!
    }
  }
  return null;  // No winner yet
}

/**
 * handleWin(player, combo)
 * Called when a player wins.
 * Highlights winning cells, updates score, shows popup.
 */
function handleWin(player, combo) {
  gameActive = false;

  // Track fastest win record
  if (fastestWin === null || movesThisGame < fastestWin) {
    fastestWin = movesThisGame;
  }

  // Highlight the 3 winning cells
  combo.forEach(i => getCell(i).classList.add('winner'));

  // Update scores
  if (player === 'X') {
    scoreX++;
    bumpScoreCard('x');
  } else {
    scoreO++;
    bumpScoreCard('o');
  }
  totalGames++;
  updateScoreDisplay();
  updateStats();

  // Sound effect
  playSound('win');

  // Determine popup message
  const isAI  = gameMode === 'pvc';
  const icon  = (player === 'X') ? '🏆' : (isAI ? '🤖' : '🏆');
  const title = isAI
    ? (player === 'X' ? 'YOU WIN!' : 'AI WINS!')
    : `PLAYER ${player} WINS!`;
  const sub   = `Moves played: ${movesThisGame} &nbsp;|&nbsp; Total games: ${totalGames}`;

  // Update status bar
  const statusMsg = isAI
    ? (player === 'X' ? '🏆 You Win!' : '🤖 Computer Wins!')
    : `🏆 Player ${player} Wins!`;
  setStatus(statusMsg, player === 'X' ? 'var(--x)' : 'var(--o)');

  // Show result popup after winning animation
  setTimeout(() => showPopup(icon, title, sub), 950);
}

/**
 * handleDraw()
 * Called when the board is full with no winner.
 */
function handleDraw() {
  gameActive = false;
  scoreDraw++;
  totalGames++;
  bumpScoreCard('d');
  updateScoreDisplay();
  updateStats();
  playSound('draw');
  setStatus("🤝 It's a Draw!", 'var(--accent)');
  setTimeout(() => showPopup('🤝', "IT'S A DRAW!", `Moves: ${movesThisGame} &nbsp;|&nbsp; Total games: ${totalGames}`), 700);
}

/**
 * resetScore()
 * Clears all scores and stats. Called from Reset Score button.
 */
function resetScore() {
  scoreX = scoreO = scoreDraw = totalGames = 0;
  fastestWin = null;
  updateScoreDisplay();
  updateStats();
  startGame();
}


/* ── 6. AI ENGINE — MINIMAX ALGORITHM ───────────────────────
   ┌─────────────────────────────────────────────────────┐
   │  ACADEMIC EXPLANATION — Minimax Algorithm           │
   │                                                     │
   │  Minimax is a recursive decision-making algorithm   │
   │  used in two-player games. The AI simulates ALL     │
   │  possible future moves on the board and picks the   │
   │  move that leads to the best outcome.               │
   │                                                     │
   │  MAX player (AI = 'O')  → wants score as HIGH as   │
   │  possible (+10 = AI wins)                           │
   │                                                     │
   │  MIN player (Human='X') → wants score as LOW as    │
   │  possible (-10 = human wins)                        │
   │                                                     │
   │  depth penalty ensures AI prefers faster wins.      │
   └─────────────────────────────────────────────────────┘
 */

/**
 * checkWin(board, player)
 * Utility: returns true if the given player has won on this board.
 */
function checkWin(b, player) {
  return WIN_COMBOS.some(([a, x, c]) =>
    b[a] === player && b[x] === player && b[c] === player
  );
}

/**
 * minimax(board, isMaximizing, depth)
 * Recursive function that evaluates every possible game state.
 *
 * @param  {Array}   b            - Current board state
 * @param  {boolean} isMaximizing - true = AI's turn, false = human's turn
 * @param  {number}  depth        - How many moves deep we are
 * @returns {number}              - Score for this board state
 */
function minimax(b, isMaximizing, depth = 0) {
  // Base cases: check if game is already over
  if (checkWin(b, 'O')) return 10 - depth;   // AI wins (sooner = higher score)
  if (checkWin(b, 'X')) return depth - 10;   // Human wins
  const empty = b.reduce((acc, v, i) => (v === '' ? [...acc, i] : acc), []);
  if (empty.length === 0) return 0;           // Draw

  if (isMaximizing) {
    // AI's turn — find the MAXIMUM score
    let best = -Infinity;
    for (const i of empty) {
      b[i] = 'O';
      best = Math.max(best, minimax(b, false, depth + 1));
      b[i] = '';  // Undo the move
    }
    return best;
  } else {
    // Human's turn — find the MINIMUM score
    let best = Infinity;
    for (const i of empty) {
      b[i] = 'X';
      best = Math.min(best, minimax(b, true, depth + 1));
      b[i] = '';  // Undo the move
    }
    return best;
  }
}

/**
 * bestMove(board)
 * Decides the AI's next move using a 3-step strategy:
 *
 * Step 1: Can AI win immediately? → take it.
 * Step 2: Is human about to win? → block it.
 * Step 3: Use Minimax to find the most optimal move.
 */
function bestMove(b) {
  const empty = b.reduce((acc, v, i) => (v === '' ? [...acc, i] : acc), []);

  // Step 1: Immediate win
  for (const i of empty) {
    b[i] = 'O';
    if (checkWin(b, 'O')) { b[i] = ''; return i; }
    b[i] = '';
  }

  // Step 2: Block human's win
  for (const i of empty) {
    b[i] = 'X';
    if (checkWin(b, 'X')) { b[i] = ''; return i; }
    b[i] = '';
  }

  // Step 3: Minimax for all remaining moves
  let bestScore = -Infinity;
  let bestPos   = empty[0];

  for (const i of empty) {
    b[i] = 'O';
    const score = minimax(b, false);
    b[i] = '';
    if (score > bestScore) {
      bestScore = score;
      bestPos   = i;
    }
  }

  return bestPos;
}


/* ── 7. SOUND EFFECTS ────────────────────────────────────────
   We use the Web Audio API to generate sounds dynamically.
   No external audio files needed — pure JavaScript sound!   */

/**
 * playSound(type)
 * Generates different tones for different game events.
 *
 * Web Audio API works by:
 * 1. Creating an AudioContext (the sound engine)
 * 2. Creating an Oscillator (the tone generator)
 * 3. Connecting through a GainNode (volume control)
 * 4. Starting and stopping the oscillator
 */
function playSound(type) {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);

    if (type === 'click_x') {
      // High-pitched click for X
      osc.frequency.setValueAtTime(600, ctx.currentTime);
      gain.gain.setValueAtTime(0.12, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1);
      osc.start();
      osc.stop(ctx.currentTime + 0.1);

    } else if (type === 'click_o') {
      // Lower click for O
      osc.frequency.setValueAtTime(380, ctx.currentTime);
      gain.gain.setValueAtTime(0.12, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1);
      osc.start();
      osc.stop(ctx.currentTime + 0.1);

    } else if (type === 'win') {
      // Victory: ascending 4-note melody
      const notes = [523, 659, 784, 1047];
      notes.forEach((freq, i) => {
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.connect(g);
        g.connect(ctx.destination);
        o.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.13);
        g.gain.setValueAtTime(0.18, ctx.currentTime + i * 0.13);
        g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.13 + 0.2);
        o.start(ctx.currentTime + i * 0.13);
        o.stop(ctx.currentTime + i * 0.13 + 0.2);
      });

    } else if (type === 'draw') {
      // Draw: descending tone
      osc.frequency.setValueAtTime(350, ctx.currentTime);
      osc.frequency.linearRampToValueAtTime(200, ctx.currentTime + 0.35);
      gain.gain.setValueAtTime(0.12, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
      osc.start();
      osc.stop(ctx.currentTime + 0.35);
    }

  } catch (e) {
    // Silently skip — some browsers block AudioContext until user interacts
  }
}


/* ── 8. UI HELPERS ───────────────────────────────────────────*/

/**
 * updateStatus()
 * Updates the status bar text to show whose turn it is.
 */
function updateStatus() {
  if (!gameActive) return;

  let msg, color;

  if (gameMode === 'pvc') {
    if (currentPlayer === 'X') {
      msg   = '🎯 Your Turn &nbsp;(X)';
      color = 'var(--x)';
    } else {
      msg   = `🤖 AI Thinking<span class="thinking-dots"><span>.</span><span>.</span><span>.</span></span>`;
      color = 'var(--o)';
    }
  } else {
    msg   = `🎯 Player ${currentPlayer}'s Turn`;
    color = (currentPlayer === 'X') ? 'var(--x)' : 'var(--o)';
  }

  setStatus(msg, color);
}

/**
 * setStatus(html, color)
 * Sets the status bar content and color.
 */
function setStatus(html, color) {
  const el = document.getElementById('status');
  el.innerHTML    = html;
  el.style.color  = color;
}

/**
 * updateScoreDisplay()
 * Refreshes the three score numbers in the scoreboard.
 */
function updateScoreDisplay() {
  document.getElementById('score-x').textContent = scoreX;
  document.getElementById('score-o').textContent = scoreO;
  document.getElementById('score-d').textContent = scoreDraw;
}

/**
 * bumpScoreCard(who)
 * Triggers the bump animation on the relevant score card
 * to provide visual feedback when score changes.
 */
function bumpScoreCard(who) {
  const selector = { x: '.x-card', o: '.o-card', d: '.draw-card' }[who];
  const el = document.querySelector(selector);
  el.classList.remove('bump');
  void el.offsetWidth;     // Force browser reflow to restart animation
  el.classList.add('bump');
}

/**
 * updateStats()
 * Refreshes the statistics panel values.
 */
function updateStats() {
  document.getElementById('stat-total').textContent   = totalGames;
  document.getElementById('stat-fastest').textContent = fastestWin ?? '—';
  document.getElementById('stat-moves').textContent   = movesThisGame;

  const rate = (totalGames > 0)
    ? `${Math.round((scoreX / totalGames) * 100)}%`
    : '—';
  document.getElementById('stat-rate').textContent = rate;
}

/**
 * showPopup(icon, title, sub)
 * Displays the game-over popup overlay.
 */
function showPopup(icon, title, sub) {
  document.getElementById('popup-icon').textContent  = icon;
  document.getElementById('popup-title').textContent = title;
  document.getElementById('popup-sub').innerHTML     = sub;
  document.getElementById('overlay').classList.add('show');
}

/**
 * closePopup()
 * Hides the popup and starts a new game.
 * Called by the "Play Again" button in the popup.
 */
function closePopup() {
  document.getElementById('overlay').classList.remove('show');
  startGame();
}


/* ── 9. THEME TOGGLE ─────────────────────────────────────────
   Switching between dark and light mode by toggling the
   'light' class on <body>. CSS variables handle all the
   color changes automatically.                             */

let isLight = false;   // Track current theme

/**
 * toggleTheme()
 * Called by the Dark/Light toggle button.
 */
function toggleTheme() {
  isLight = !isLight;
  document.body.classList.toggle('light', isLight);
  document.getElementById('theme-btn').textContent =
    isLight ? '☾ Dark Mode' : '☀ Light Mode';
}


/* ── 10. INITIALIZATION ──────────────────────────────────────
   Run when the page loads.
   Build the board and start the first game.               */
buildBoard();
startGame();