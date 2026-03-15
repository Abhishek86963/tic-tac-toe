"""
╔══════════════════════════════════════════════════════════════════╗
║          TIC TAC TOE SMART GAME IN PYTHON                       ║
║          tic_tac_toe.py  —  Desktop Version (Tkinter)           ║
╚══════════════════════════════════════════════════════════════════╝

HOW TO RUN:
    python tic_tac_toe.py

REQUIREMENTS:
    Python 3.x  (Tkinter is built-in, no pip install needed)

ACADEMIC NOTE:
    This is the desktop version of the game.
    The web version (index.html + style.css + script.js)
    runs in any browser and can be hosted on GitHub Pages.
"""

import tkinter as tk
from tkinter import font
import math
import time
import platform
import os

# ─── SOUND ──────────────────────────────────────────────────────────────────────
def play_sound(sound_type):
    """Play platform-specific sound effects."""
    try:
        if platform.system() == "Windows":
            import winsound
            sounds = {"click": (800, 60), "draw": (300, 300)}
            if sound_type in sounds:
                winsound.Beep(*sounds[sound_type])
            elif sound_type == "win":
                for f in [523, 659, 784, 1047]:
                    winsound.Beep(f, 120)
        elif platform.system() == "Darwin":
            if sound_type == "win":
                os.system("afplay /System/Library/Sounds/Glass.aiff &")
            elif sound_type == "click":
                os.system("afplay /System/Library/Sounds/Tink.aiff &")
    except Exception:
        pass


# ─── THEMES ─────────────────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "bg": "#080c14", "panel": "#131a28", "border": "#1e2d45",
        "x": "#ff4d6d", "o": "#00e5c3", "accent": "#4f8fff",
        "win": "#ffd60a", "text": "#e2e8f0", "muted": "#64748b",
        "cell": "#0e1420", "cell_hover": "#1a2540",
        "score_bg": "#131a28", "btn": "#4f8fff", "btn_fg": "#ffffff",
    },
    "light": {
        "bg": "#f0f4ff", "panel": "#ffffff", "border": "#c5cae9",
        "x": "#e63946", "o": "#0891b2", "accent": "#4361ee",
        "win": "#f59e0b", "text": "#1a1a2e", "muted": "#64748b",
        "cell": "#ffffff", "cell_hover": "#eef2ff",
        "score_bg": "#ffffff", "btn": "#4361ee", "btn_fg": "#ffffff",
    }
}

# ─── AI ENGINE — MINIMAX ─────────────────────────────────────────────────────────
class AIEngine:
    """
    MINIMAX ALGORITHM:
    Recursively explores all possible moves.
    Returns the best move index for the AI ('O').
    """
    WIN_COMBOS = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]

    def check_win(self, board, player):
        return any(all(board[i] == player for i in c) for c in self.WIN_COMBOS)

    def available(self, board):
        return [i for i, v in enumerate(board) if v == ""]

    def minimax(self, board, is_max, depth=0):
        if self.check_win(board, "O"): return 10 - depth
        if self.check_win(board, "X"): return depth - 10
        empty = self.available(board)
        if not empty: return 0

        if is_max:
            best = -math.inf
            for i in empty:
                board[i] = "O"
                best = max(best, self.minimax(board, False, depth+1))
                board[i] = ""
            return best
        else:
            best = math.inf
            for i in empty:
                board[i] = "X"
                best = min(best, self.minimax(board, True, depth+1))
                board[i] = ""
            return best

    def best_move(self, board):
        empty = self.available(board)
        # Win immediately
        for i in empty:
            board[i] = "O"
            if self.check_win(board, "O"): board[i] = ""; return i
            board[i] = ""
        # Block human
        for i in empty:
            board[i] = "X"
            if self.check_win(board, "X"): board[i] = ""; return i
            board[i] = ""
        # Minimax
        best_score, best_pos = -math.inf, empty[0]
        for i in empty:
            board[i] = "O"
            s = self.minimax(board, False)
            board[i] = ""
            if s > best_score:
                best_score, best_pos = s, i
        return best_pos


# ─── MAIN APP ────────────────────────────────────────────────────────────────────
class TicTacToeApp:
    WIN_COMBOS = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe Smart Game")
        self.root.resizable(False, False)

        # State
        self.dark        = True
        self.theme       = THEMES["dark"]
        self.mode        = tk.StringVar(value="pvp")
        self.board       = [""] * 9
        self.current     = "X"
        self.active      = False
        self.animating   = False

        # Scores & stats
        self.score_x = self.score_o = self.score_d = 0
        self.total = self.moves = 0
        self.fastest = None

        # Fonts
        self.f_title  = font.Font(family="Georgia",     size=20, weight="bold")
        self.f_sym    = font.Font(family="Georgia",     size=42, weight="bold")
        self.f_label  = font.Font(family="Courier New", size=10, weight="bold")
        self.f_btn    = font.Font(family="Courier New", size=9,  weight="bold")
        self.f_score  = font.Font(family="Georgia",     size=20, weight="bold")
        self.f_stat   = font.Font(family="Courier New", size=9)
        self.f_status = font.Font(family="Georgia",     size=12, weight="bold", slant="italic")

        self.ai = AIEngine()
        self._build_ui()
        self.apply_theme()
        self.start_game()

    # ── UI BUILD ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.root.configure(bg=self.theme["bg"])
        self.outer = tk.Frame(self.root, bg=self.theme["bg"])
        self.outer.pack(padx=28, pady=18)
        self._header()
        self._mode_selector()
        self._scoreboard()
        self._board()
        self._status_bar()
        self._controls()
        self._stats()

    def _header(self):
        f = tk.Frame(self.outer, bg=self.theme["bg"])
        f.pack(fill="x", pady=(0, 8))
        self.lbl_title = tk.Label(f, text="⚡ TIC TAC TOE",
            font=self.f_title, bg=self.theme["bg"], fg=self.theme["text"])
        self.lbl_title.pack()
        self.lbl_sub = tk.Label(f, text="SMART GAME  ·  PYTHON PROJECT",
            font=self.f_stat, bg=self.theme["bg"], fg=self.theme["muted"])
        self.lbl_sub.pack()

    def _mode_selector(self):
        f = tk.Frame(self.outer, bg=self.theme["bg"])
        f.pack(pady=(0, 10))
        tk.Label(f, text="MODE:", font=self.f_label,
                 bg=self.theme["bg"], fg=self.theme["muted"]).pack(side="left", padx=(0,8))
        self.rb_pvp = tk.Radiobutton(f, text="👥 Player vs Player",
            variable=self.mode, value="pvp", command=self._change_mode,
            font=self.f_btn, bg=self.theme["bg"], fg=self.theme["text"],
            selectcolor=self.theme["panel"], activebackground=self.theme["bg"])
        self.rb_pvp.pack(side="left", padx=4)
        self.rb_pvc = tk.Radiobutton(f, text="🤖 vs Computer",
            variable=self.mode, value="pvc", command=self._change_mode,
            font=self.f_btn, bg=self.theme["bg"], fg=self.theme["text"],
            selectcolor=self.theme["panel"], activebackground=self.theme["bg"])
        self.rb_pvc.pack(side="left", padx=4)
        self.mode_widgets = [self.rb_pvp, self.rb_pvc]

    def _scoreboard(self):
        f = tk.Frame(self.outer, bg=self.theme["bg"])
        f.pack(fill="x", pady=(0,10))

        def card(parent, label, color_key):
            blk = tk.Frame(parent, bg=self.theme["score_bg"])
            blk.pack(side="left", expand=True, fill="both", padx=5, pady=2)
            lbl = tk.Label(blk, text=label, font=self.f_label,
                           bg=self.theme["score_bg"], fg=self.theme[color_key])
            lbl.pack(pady=(8,0))
            num = tk.Label(blk, text="0", font=self.f_score,
                           bg=self.theme["score_bg"], fg=self.theme[color_key])
            num.pack(pady=(0,8))
            return blk, lbl, num

        self.sx_f, self.sx_l, self.sx_n = card(f, "✕  X WINS", "x")
        self.sd_f, self.sd_l, self.sd_n = card(f, "◈  DRAWS",  "accent")
        self.so_f, self.so_l, self.so_n = card(f, "○  O WINS", "o")

    def _board(self):
        wrap = tk.Frame(self.outer, bg=self.theme["panel"], padx=3, pady=3)
        wrap.pack(pady=6)
        self.CELL = 108
        self.GAP  = 4
        total = self.CELL * 3 + self.GAP * 2

        self.canvas = tk.Canvas(wrap, width=total, height=total,
                                bg=self.theme["panel"], bd=0, highlightthickness=0)
        self.canvas.pack()
        self.rects = []
        self.texts = []
        self.hover = [-1]

        for row in range(3):
            for col in range(3):
                idx = row * 3 + col
                x1 = col * (self.CELL + self.GAP)
                y1 = row * (self.CELL + self.GAP)
                r = self.canvas.create_rectangle(
                    x1, y1, x1+self.CELL, y1+self.CELL,
                    fill=self.theme["cell"], outline=self.theme["panel"], width=self.GAP,
                    tags=(f"c{idx}", "cell"))
                t = self.canvas.create_text(
                    x1+self.CELL//2, y1+self.CELL//2,
                    text="", font=self.f_sym, fill=self.theme["x"], tags=f"t{idx}")
                self.rects.append(r)
                self.texts.append(t)

        self.canvas.bind("<Button-1>", self._click)
        self.canvas.bind("<Motion>",   self._hover_move)
        self.canvas.bind("<Leave>",    self._hover_leave)

    def _status_bar(self):
        self.lbl_status = tk.Label(self.outer, text="",
            font=self.f_status, bg=self.theme["bg"], fg=self.theme["accent"])
        self.lbl_status.pack(pady=(5,3))

    def _controls(self):
        f = tk.Frame(self.outer, bg=self.theme["bg"])
        f.pack(pady=(3,6))

        def btn(parent, text, cmd, color):
            b = tk.Button(parent, text=text, command=cmd,
                font=self.f_btn, bg=color, fg="#fff",
                relief="flat", bd=0, padx=10, pady=6, cursor="hand2",
                activebackground=color, activeforeground="#fff")
            b.bind("<Enter>", lambda e: b.config(relief="groove"))
            b.bind("<Leave>", lambda e: b.config(relief="flat"))
            return b

        btn(f, "↺ Restart",     self.start_game,  "#27AE60").pack(side="left", padx=5)
        btn(f, "⊘ Reset Score", self.reset_score,  "#E67E22").pack(side="left", padx=5)
        self.btn_theme = btn(f, "☀ Light Mode", self.toggle_theme, "#7B68EE")
        self.btn_theme.pack(side="left", padx=5)

    def _stats(self):
        f = tk.Frame(self.outer, bg=self.theme["panel"])
        f.pack(fill="x", pady=(3,0))
        tk.Label(f, text="📊  STATISTICS", font=self.f_label,
                 bg=self.theme["panel"], fg=self.theme["accent"]).pack(anchor="w", padx=10, pady=(8,2))

        inner = tk.Frame(f, bg=self.theme["panel"])
        inner.pack(fill="x", padx=10, pady=(0,8))

        def row(label):
            r = tk.Frame(inner, bg=self.theme["panel"])
            r.pack(fill="x", pady=1)
            tk.Label(r, text=label, font=self.f_stat, bg=self.theme["panel"],
                     fg=self.theme["muted"], width=24, anchor="w").pack(side="left")
            v = tk.Label(r, text="—", font=self.f_stat, bg=self.theme["panel"],
                         fg=self.theme["text"], anchor="w")
            v.pack(side="left")
            return v

        self.s_total   = row("Total Games Played:")
        self.s_fastest = row("Fastest Win (moves):")
        self.s_moves   = row("Moves This Game:")
        self.s_rate    = row("X Win Rate:")
        self.stat_frame = f

    # ── THEME ─────────────────────────────────────────────────────────────────────
    def apply_theme(self):
        t = self.theme
        for w in [self.root, self.outer]:
            w.configure(bg=t["bg"])
        self.lbl_title.config(bg=t["bg"], fg=t["text"])
        self.lbl_sub.config(bg=t["bg"], fg=t["muted"])
        for rb in self.mode_widgets:
            rb.config(bg=t["bg"], fg=t["text"], selectcolor=t["panel"],
                      activebackground=t["bg"])
        for frm, lbl, num, ck in [
            (self.sx_f, self.sx_l, self.sx_n, "x"),
            (self.sd_f, self.sd_l, self.sd_n, "accent"),
            (self.so_f, self.so_l, self.so_n, "o"),
        ]:
            frm.config(bg=t["score_bg"])
            lbl.config(bg=t["score_bg"], fg=t[ck])
            num.config(bg=t["score_bg"], fg=t[ck])
        self.canvas.config(bg=t["panel"])
        for i, r in enumerate(self.rects):
            self.canvas.itemconfig(r, fill=t["cell"], outline=t["panel"])
            sym = self.board[i]
            self.canvas.itemconfig(self.texts[i],
                fill=t["x"] if sym == "X" else t["o"])
        self.lbl_status.config(bg=t["bg"])
        self.stat_frame.config(bg=t["panel"])

    def toggle_theme(self):
        self.dark = not self.dark
        self.theme = THEMES["dark"] if self.dark else THEMES["light"]
        self.btn_theme.config(text="☀ Light Mode" if self.dark else "☾ Dark Mode")
        self.apply_theme()
        self._update_status()

    # ── GAME LOGIC ────────────────────────────────────────────────────────────────
    def start_game(self):
        self.board   = [""] * 9
        self.current = "X"
        self.active  = True
        self.moves   = 0
        for i in range(9):
            self.canvas.itemconfig(self.rects[i], fill=self.theme["cell"])
            self.canvas.itemconfig(self.texts[i],  text="")
        self._update_status()
        self._update_stats()

    def _change_mode(self):
        self.reset_score()
        self.start_game()

    def _idx_from_xy(self, x, y):
        c = x // (self.CELL + self.GAP)
        r = y // (self.CELL + self.GAP)
        if 0 <= r < 3 and 0 <= c < 3:
            return r * 3 + c
        return -1

    def _click(self, event):
        if not self.active or self.animating: return
        idx = self._idx_from_xy(event.x, event.y)
        if idx == -1 or self.board[idx] != "": return
        self._make_move(idx, self.current)

    def _make_move(self, idx, player):
        self.board[idx] = player
        self.moves += 1
        play_sound("click")
        self._animate_sym(idx, player)

        combo = self._winner_combo()
        if combo:
            self._handle_win(player, combo); return
        if "" not in self.board:
            self._handle_draw(); return

        self.current = "O" if player == "X" else "X"
        self._update_status()
        self._update_stats()

        if self.mode.get() == "pvc" and self.current == "O" and self.active:
            self.root.after(420, self._ai_turn)

    def _ai_turn(self):
        if not self.active: return
        idx = self.ai.best_move(self.board[:])
        self._make_move(idx, "O")

    def _winner_combo(self):
        for combo in self.WIN_COMBOS:
            a, b, c = combo
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                return combo
        return None

    def _handle_win(self, player, combo):
        self.active = False
        if self.fastest is None or self.moves < self.fastest:
            self.fastest = self.moves
        play_sound("win")
        self._flash_cells(combo)
        if player == "X": self.score_x += 1; self.sx_n.config(text=str(self.score_x))
        else:              self.score_o += 1; self.so_n.config(text=str(self.score_o))
        self.total += 1
        msg = ("🏆 You Win!" if player=="X" else "🤖 AI Wins!") if self.mode.get()=="pvc" else f"🏆 Player {player} Wins!"
        color = self.theme["x"] if player == "X" else self.theme["o"]
        self.lbl_status.config(text=msg, fg=color)
        self._update_stats()
        self.root.after(1000, lambda: self._popup(msg))

    def _handle_draw(self):
        self.active = False
        self.score_d += 1; self.total += 1
        self.sd_n.config(text=str(self.score_d))
        play_sound("draw")
        self.lbl_status.config(text="🤝 It's a Draw!", fg=self.theme["accent"])
        self._update_stats()
        self.root.after(650, lambda: self._popup("🤝 Draw!"))

    def reset_score(self):
        self.score_x = self.score_o = self.score_d = self.total = 0
        self.fastest = None
        self.sx_n.config(text="0"); self.so_n.config(text="0"); self.sd_n.config(text="0")
        self._update_stats()

    # ── ANIMATIONS ────────────────────────────────────────────────────────────────
    def _animate_sym(self, idx, player):
        color  = self.theme["x"] if player == "X" else self.theme["o"]
        symbol = "✕" if player == "X" else "○"
        self.canvas.itemconfig(self.rects[idx], fill=self.theme["cell_hover"])
        sizes = [10, 22, 34, 44, 50, 46]

        def step(i):
            if i < len(sizes):
                f = font.Font(family="Georgia", size=sizes[i], weight="bold")
                self.canvas.itemconfig(self.texts[idx], text=symbol, fill=color, font=f)
                self.root.after(35, lambda: step(i+1))
            else:
                self.canvas.itemconfig(self.rects[idx], fill=self.theme["cell"])
                self.canvas.itemconfig(self.texts[idx], text=symbol, fill=color, font=self.f_sym)

        self.animating = True
        step(0)
        self.root.after(240, lambda: setattr(self, "animating", False))

    def _flash_cells(self, combo):
        win_color = self.theme["win"]
        def flash(n, hi):
            if n <= 0:
                for i in combo:
                    self.canvas.itemconfig(self.rects[i], fill="#2d2a00" if self.dark else "#fff8dc")
                return
            c = win_color if hi else self.theme["cell"]
            for i in combo: self.canvas.itemconfig(self.rects[i], fill=c)
            self.root.after(175, lambda: flash(n-1, not hi))
        flash(6, True)

    def _hover_move(self, event):
        if not self.active: return
        idx  = self._idx_from_xy(event.x, event.y)
        prev = self.hover[0]
        if idx == prev: return
        if prev != -1 and self.board[prev] == "":
            self.canvas.itemconfig(self.rects[prev], fill=self.theme["cell"])
        if idx != -1 and self.board[idx] == "":
            self.canvas.itemconfig(self.rects[idx], fill=self.theme["cell_hover"])
            self.canvas.config(cursor="hand2")
        else:
            self.canvas.config(cursor="")
        self.hover[0] = idx

    def _hover_leave(self, event):
        prev = self.hover[0]
        if prev != -1 and self.board[prev] == "":
            self.canvas.itemconfig(self.rects[prev], fill=self.theme["cell"])
        self.hover[0] = -1

    # ── STATUS & STATS ────────────────────────────────────────────────────────────
    def _update_status(self):
        if not self.active: return
        p = self.current
        if self.mode.get() == "pvc":
            msg   = "🎯 Your Turn (X)" if p == "X" else "🤖 AI Thinking..."
        else:
            msg = f"🎯 Player {p}'s Turn"
        color = self.theme["x"] if p == "X" else self.theme["o"]
        self.lbl_status.config(text=msg, fg=color)

    def _update_stats(self):
        self.s_total.config(text=str(self.total))
        self.s_fastest.config(text=str(self.fastest) if self.fastest else "—")
        self.s_moves.config(text=str(self.moves))
        rate = f"{round(self.score_x/self.total*100)}%" if self.total else "—"
        self.s_rate.config(text=rate)

    # ── POPUP ─────────────────────────────────────────────────────────────────────
    def _popup(self, message):
        pop = tk.Toplevel(self.root)
        pop.title("Game Over")
        pop.resizable(False, False)
        pop.configure(bg=self.theme["panel"])
        pop.grab_set()
        t = self.theme
        tk.Label(pop, text="GAME OVER", font=self.f_label,
                 bg=t["panel"], fg=t["muted"]).pack(padx=36, pady=(18,4))
        tk.Label(pop, text=message, font=self.f_status,
                 bg=t["panel"], fg=t["text"]).pack(padx=36, pady=4)
        tk.Label(pop, text=f"Moves: {self.moves}   |   Total: {self.total}",
                 font=self.f_stat, bg=t["panel"], fg=t["muted"]).pack(pady=4)

        def close():
            pop.destroy(); self.start_game()

        tk.Button(pop, text="▶  PLAY AGAIN", command=close,
                  font=self.f_btn, bg=t["btn"], fg=t["btn_fg"],
                  relief="flat", padx=18, pady=8, cursor="hand2").pack(pady=(8,18))
        self.root.update_idletasks()
        px = self.root.winfo_x() + self.root.winfo_width()//2 - 130
        py = self.root.winfo_y() + self.root.winfo_height()//2 - 80
        pop.geometry(f"+{px}+{py}")


# ─── ENTRY POINT ────────────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"490x700+{(sw-490)//2}+{(sh-700)//2}")
    TicTacToeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()