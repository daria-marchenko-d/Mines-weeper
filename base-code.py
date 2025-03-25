import tkinter as tk
import random
import time

class Demineur:
    def __init__(self, root):
        self.root = root
        self.root.title("Démineur")
        self.difficulty = {
            "Facile": (9, 9, 10),
            "Moyen": (16, 16, 40),
            "Difficile": (16, 30, 99)
        }
        self.start_time = None
        self.running = False
        self.create_menu()

    def create_menu(self):
        """Créer le menu de sélection du niveau."""
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack()
        
        tk.Label(self.menu_frame, text="Choisissez la difficulté :").pack()
        for level in self.difficulty:
            tk.Button(self.menu_frame, text=level, command=lambda l=level: self.start_game(l)).pack()

    def start_game(self, level):
        """Démarre une nouvelle partie avec le niveau choisi."""
        self.level = level
        self.rows, self.cols, self.mines_count = self.difficulty[level]

        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        if hasattr(self, "game_frame"):
            self.game_frame.destroy()

        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack()

        self.timer_label = tk.Label(self.game_frame, text="Temps: 0s")
        self.timer_label.grid(row=0, column=0, columnspan=self.cols)

        # Ajouter les labels pour les mines, drapeaux et points d'interrogation
        self.mines_label = tk.Label(self.game_frame, text=f"Mines: {self.mines_count}")
        self.mines_label.grid(row=1, column=0, columnspan=self.cols // 3)

        self.flags_label = tk.Label(self.game_frame, text="Drapeaux: 0")
        self.flags_label.grid(row=1, column=self.cols // 3, columnspan=self.cols // 3)

        self.questions_label = tk.Label(self.game_frame, text="Points d'interrogation: 0")
        self.questions_label.grid(row=1, column=2 * (self.cols // 3), columnspan=self.cols // 3)

        self.restart_button = tk.Button(self.game_frame, text="Réinitialiser", command=lambda: self.start_game(self.level))
        self.restart_button.grid(row=0, column=self.cols - 1)

        self.board_frame = tk.Frame(self.game_frame)
        self.board_frame.grid(row=2, column=0, columnspan=self.cols)

        self.board = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.mines = set()
        self.first_click = True
        self.running = False
        self.flags_count = 0
        self.question_marks_count = 0

        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(self.board_frame, width=2, height=1, command=lambda x=r, y=c: self.reveal(x, y))
                btn.bind("<Button-3>", lambda e, x=r, y=c: self.flag(x, y))  # Correction ici
                btn.grid(row=r, column=c)
                self.board[r][c] = {"btn": btn, "mine": False, "revealed": False, "flag": 0}

        self.update_timer()

    def place_mines(self, safe_r, safe_c):
        """Place les mines après le premier clic."""
        available_positions = [(r, c) for r in range(self.rows) for c in range(self.cols) if (r, c) != (safe_r, safe_c)]
        self.mines = set(random.sample(available_positions, self.mines_count))

        for r, c in self.mines:
            self.board[r][c]["mine"] = True

    def reveal(self, r, c):
        """Révèle une case et applique les règles du jeu."""
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
            self.board[r][c]["btn"].config(text=str(mines_adj))
        else:
            self.reveal_adjacent(r, c)

        if self.check_win():
            self.game_over(True)

    def count_adjacent_mines(self, r, c):
        """Compte le nombre de mines adjacentes à une case donnée."""
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if (dr == 0 and dc == 0) or not (0 <= r+dr < self.rows and 0 <= c+dc < self.cols):
                    continue
                if self.board[r+dr][c+dc]["mine"]:
                    count += 1
        return count

    def reveal_adjacent(self, r, c):
        """Révèle les cases vides adjacentes (récursivité)."""
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols and not self.board[nr][nc]["revealed"]:
                    self.reveal(nr, nc)

    def flag(self, r, c):
        """Ajoute ou enlève un drapeau ou un point d'interrogation sur une case."""
        if self.board[r][c]["revealed"]:
            return

        current_flag = self.board[r][c]["flag"]
        new_flag = (current_flag + 1) % 3  # Cycle entre 0 (vide), 1 (drapeau), 2 (point d'interrogation)
        self.board[r][c]["flag"] = new_flag

        # Mettre à jour le texte du bouton
        symbols = ["", "🚩", "?"]
        self.board[r][c]["btn"].config(text=symbols[new_flag])

        # Mettre à jour les compteurs
        if current_flag == 0 and new_flag == 1:  # Vide → Drapeau
            self.flags_count += 1
        elif current_flag == 1 and new_flag == 2:  # Drapeau → Point d'interrogation
            self.flags_count -= 1
            self.question_marks_count += 1
        elif current_flag == 2 and new_flag == 0:  # Point d'interrogation → Vide
            self.question_marks_count -= 1

        # Mettre à jour les labels
        self.update_labels()

    def check_win(self):
        """Vérifie si toutes les cases non minées sont révélées."""
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.board[r][c]["mine"] and not self.board[r][c]["revealed"]:
                    return False
        return True

    def game_over(self, won):
        """Affiche le résultat et arrête le jeu."""
        self.running = False
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c]["mine"]:
                    self.board[r][c]["btn"].config(text="💣")
                self.board[r][c]["btn"].config(state=tk.DISABLED)

        message = "Victoire ! 🎉" if won else "Perdu... 💥"
        self.timer_label.config(text=message)

    def update_timer(self):
        """Mise à jour du chronomètre."""
        if self.running and self.start_time:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Temps: {elapsed_time}s")
        self.root.after(1000, self.update_timer)

    def update_labels(self):
        """Met à jour les labels des mines, drapeaux et points d'interrogation."""
        self.flags_label.config(text=f"Drapeaux: {self.flags_count}")
        self.questions_label.config(text=f"Points d'interrogation: {self.question_marks_count}")
        self.mines_label.config(text=f"Mines: {self.mines_count - self.flags_count}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Demineur(root)
    root.mainloop()
