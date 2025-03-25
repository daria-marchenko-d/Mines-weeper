import tkinter as tk
import random
import time
from tkinter import messagebox

class Demineur:
    COLORS = ["", "blue", "green", "red", "purple", "maroon", "cyan", "black", "gray"]

    def __init__(self, root):
        self.root = root
        self.root.title("Démineur")
        self.difficulty = {"Facile": (9, 9, 10), "Moyen": (16, 16, 40), "Difficile": (16, 30, 99)}
        self.start_time = None
        self.running = False
        self.create_menu()

    def create_menu(self):
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack()
        
        tk.Label(self.menu_frame, text="Choisissez la difficulté :").pack()
        for level in self.difficulty:
            tk.Button(self.menu_frame, text=level, command=lambda l=level: self.start_game(l)).pack()

    def start_game(self, level):
        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        if hasattr(self, "game_frame"):
            if not messagebox.askyesno("Réinitialisation", "Voulez-vous recommencer la partie ?"):
                return
            self.game_frame.destroy()

        self.level = level
        self.rows, self.cols, self.mines_count = self.difficulty[level]
        self.remaining_flags = self.mines_count
        self.first_click = True
        self.running = False

        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack()

        self.timer_label = tk.Label(self.game_frame, text="Temps: 0s")
        self.timer_label.grid(row=0, column=0, columnspan=self.cols // 2)

        self.flag_label = tk.Label(self.game_frame, text=f"Drapeaux restants: {self.remaining_flags}")
        self.flag_label.grid(row=0, column=self.cols // 2, columnspan=self.cols // 2)

        self.restart_button = tk.Button(self.game_frame, text="🙂", command=lambda: self.start_game(self.level))
        self.restart_button.grid(row=0, column=self.cols - 1)

        self.board_frame = tk.Frame(self.game_frame)
        self.board_frame.grid(row=1, column=0, columnspan=self.cols)

        self.board = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.mines = set()

        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(self.board_frame, width=2, height=1, command=lambda x=r, y=c: self.reveal(x, y))
                btn.bind("<Button-3>", lambda e, x=r, y=c: self.flag(x, y))
                btn.grid(row=r, column=c)
                self.board[r][c] = {"btn": btn, "mine": False, "revealed": False, "flag": 0}

        self.update_timer()

    def place_mines(self, safe_r, safe_c):
        available_positions = [(r, c) for r in range(self.rows) for c in range(self.cols) if (r, c) != (safe_r, safe_c)]
        self.mines = set(random.sample(available_positions, self.mines_count))
        for r, c in self.mines:
            self.board[r][c]["mine"] = True

    def reveal(self, r, c):
        if self.first_click:
            self.place_mines(r, c)
            self.first_click = False
            self.start_time = time.time()
            self.running = True

        if self.board[r][c]["revealed"] or self.board[r][c]["flag"] > 0:
            return

        self.board[r][c]["revealed"] = True
        self.board[r][c]["btn"].config(relief=tk.SUNKEN)

        if self.board[r][c]["mine"]:
            self.board[r][c]["btn"].config(text="💣", bg="red")
            self.game_over(False)
            return

        mines_adj = self.count_adjacent_mines(r, c)
        if mines_adj > 0:
            self.board[r][c]["btn"].config(text=str(mines_adj), fg=self.COLORS[mines_adj])
        else:
            self.reveal_adjacent(r, c)

        if self.check_win():
            self.game_over(True)

    def count_adjacent_mines(self, r, c):
        return sum((r+dr, c+dc) in self.mines for dr in [-1, 0, 1] for dc in [-1, 0, 1] if (dr, dc) != (0, 0))

    def reveal_adjacent(self, r, c):
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols and not self.board[nr][nc]["revealed"]:
                    self.reveal(nr, nc)

    def flag(self, r, c):
        if self.board[r][c]["revealed"]:
            return

        self.remaining_flags += -1 if self.board[r][c]["flag"] == 0 else (1 if self.board[r][c]["flag"] == 1 else 0)
        self.board[r][c]["flag"] = (self.board[r][c]["flag"] + 1) % 3
        symbols = ["", "🚩", "?"]
        self.board[r][c]["btn"].config(text=symbols[self.board[r][c]["flag"]])
        self.flag_label.config(text=f"Drapeaux restants: {self.remaining_flags}")

    def check_win(self):
        return all(self.board[r][c]["revealed"] or self.board[r][c]["mine"] for r in range(self.rows) for c in range(self.cols))

    def game_over(self, won):
        self.running = False
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c]["mine"]:
                    self.board[r][c]["btn"].config(text="💣", bg="gray")
                elif not self.board[r][c]["revealed"]:
                    mines_adj = self.count_adjacent_mines(r, c)
                    self.board[r][c]["btn"].config(text=str(mines_adj) if mines_adj > 0 else "", fg=self.COLORS[mines_adj])
                self.board[r][c]["btn"].config(state=tk.DISABLED)

        self.timer_label.config(text="Victoire ! 🎉" if won else "Perdu... 💥")

    def update_timer(self):
        if self.running and self.start_time:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Temps: {elapsed_time}s")
        self.root.after(1000, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    app = Demineur(root)
    root.mainloop()
