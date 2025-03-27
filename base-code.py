import tkinter as tk
import random
import time
from PIL import Image, ImageTk  # Pour les animations plus avancées (optionnel)

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

        # Initialiser les attributs nécessaires
        self.first_click = True
        self.board = []
        self.flags_count = 0
        self.question_marks_count = 0

        self.create_menu()

    def create_menu(self):
        """Créer le menu de sélection du niveau."""
        if hasattr(self, "game_frame"):
            self.game_frame.destroy()  # Détruire le cadre de jeu s'il existe

        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(fill=tk.BOTH, expand=True)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        tk.Label(self.menu_frame, text="Choisissez la difficulté :").pack(pady=20)
        for level in self.difficulty:
            tk.Button(self.menu_frame, text=level, command=lambda l=level: self.start_game(l)).pack(pady=10)

    def start_game(self, level):
        """Démarre une nouvelle partie avec le niveau choisi."""
        self.level = level
        self.rows, self.cols, self.mines_count = self.difficulty[level]

        # Réinitialiser les attributs pour une nouvelle partie
        self.first_click = True
        self.board = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.flags_count = 0
        self.question_marks_count = 0

        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        if hasattr(self, "game_frame"):
            self.game_frame.destroy()

        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        # Configurer les poids pour rendre le cadre responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.game_frame.grid_rowconfigure(2, weight=1)
        self.game_frame.grid_columnconfigure(0, weight=1)

        self.timer_label = tk.Label(self.game_frame, text="Temps: 0s")
        self.timer_label.grid(row=0, column=0, columnspan=self.cols, sticky="nsew")

        # Configurer les colonnes pour les labels
        self.game_frame.grid_columnconfigure(0, weight=1)  # Colonne pour "Mines"
        self.game_frame.grid_columnconfigure(1, weight=1)  # Colonne pour "Drapeaux"
        self.game_frame.grid_columnconfigure(2, weight=1)  # Colonne pour "Points d'interrogation"

        # Ajouter les labels pour les mines, drapeaux et points d'interrogation
        self.mines_label = tk.Label(self.game_frame, text=f"Mines: {self.mines_count}", anchor="center")
        self.mines_label.grid(row=1, column=0, sticky="nsew")

        self.flags_label = tk.Label(self.game_frame, text="Drapeaux: 0", anchor="center")
        self.flags_label.grid(row=1, column=1, sticky="nsew")

        self.questions_label = tk.Label(self.game_frame, text="Points d'interrogation: 0", anchor="center")
        self.questions_label.grid(row=1, column=2, sticky="nsew")

        self.restart_button = tk.Button(self.game_frame, text="Réinitialiser", command=lambda: self.start_game(self.level))
        self.restart_button.grid(row=0, column=self.cols - 1, sticky="nsew")

        self.board_frame = tk.Frame(self.game_frame)
        self.board_frame.grid(row=2, column=0, columnspan=self.cols, sticky="nsew")

        # Configurer les poids pour le plateau de jeu
        for r in range(self.rows):
            self.board_frame.grid_rowconfigure(r, weight=1)
        for c in range(self.cols):
            self.board_frame.grid_columnconfigure(c, weight=1)

        # Créer les boutons du plateau de jeu
        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(self.board_frame, width=2, height=1, command=lambda x=r, y=c: self.reveal(x, y))
                btn.bind("<Button-3>", lambda e, x=r, y=c: self.flag(x, y))
                btn.grid(row=r, column=c, sticky="nsew")
                self.board[r][c] = {"btn": btn, "mine": False, "revealed": False, "flag": 0}

        # Ajouter un bouton "Retour" en bas des cases
        self.back_button = tk.Button(self.game_frame, text="Retour", command=self.create_menu)
        self.back_button.grid(row=3, column=0, columnspan=self.cols, sticky="nsew")

        # Configurer les poids pour les lignes et colonnes des labels
        self.game_frame.grid_rowconfigure(1, weight=1)  # Ligne des labels
        self.game_frame.grid_columnconfigure(0, weight=1)  # Colonne des labels
        self.game_frame.grid_columnconfigure(1, weight=1)
        self.game_frame.grid_columnconfigure(2, weight=1)

        # Configurer la ligne du bouton "Retour" pour qu'elle soit responsive
        self.game_frame.grid_rowconfigure(3, weight=1)

        self.update_timer()

    def place_mines(self, safe_r, safe_c):
        """Place les mines après le premier clic."""
        available_positions = [(r, c) for r in range(self.rows) for c in range(self.cols) if (r, c) != (safe_r, safe_c)]
        self.mines = set(random.sample(available_positions, self.mines_count))

        for r, c in self.mines:
            self.board[r][c]["mine"] = True

    def reveal(self, r, c):
        """Révèle une case et applique les règles du jeu avec animation."""
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
            # Animation d'explosion pour la bombe cliquée
            self.animate_explosion(r, c, immediate=True)
            self.disable_all_interactions()  # Désactiver toutes les interactions après avoir cliqué sur une bombe
            return

        # Animation de dissipation du nuage pour les chiffres
        mines_adj = self.count_adjacent_mines(r, c)
        if mines_adj > 0:
            self.animate_reveal(r, c, mines_adj)
        else:
            # Pas d'animation pour les cases vides
            self.board[r][c]["btn"].config(text="")
            self.reveal_adjacent(r, c)

        if self.check_win():
            self.game_over(True)

    def disable_all_interactions(self):
        """Désactive toutes les interactions après avoir cliqué sur une bombe."""
        for r in range(self.rows):
            for c in range(self.cols):
                btn = self.board[r][c]["btn"]
                btn.config(state=tk.DISABLED)
                btn.unbind("<Button-1>")  # Désactiver les clics gauche
                btn.unbind("<Button-3>")  # Désactiver les clics droit

    def animate_reveal(self, r, c, mines_adj):
        """Anime la dissipation d'un nuage pour révéler le chiffre."""
        btn = self.board[r][c]["btn"]
        # Séquence d'animation: nuage qui se dissipe graduellement
        cloud_stages = ["☁️", "🌫️", "💨", str(mines_adj)]
        
        def show_next_stage(stage_index=0):
            if stage_index < len(cloud_stages):
                btn.config(text=cloud_stages[stage_index])
                self.root.after(150, show_next_stage, stage_index + 1)
        
        show_next_stage()

    def animate_explosion(self, r, c, immediate=False):
        """Anime l'explosion d'une bombe."""
        btn = self.board[r][c]["btn"]
        # Séquence d'animation: explosion
        explosion_stages = ["💣", "💥"]
        
        def show_explosion():
            btn.config(text=explosion_stages[1], bg="red")
            if not immediate:
                # Si ce n'est pas la bombe cliquée directement, jouer un son serait approprié ici
                pass
        
        # Pour la bombe cliquée, exploser immédiatement
        if immediate:
            btn.config(text=explosion_stages[0], bg="red")
            self.root.after(300, show_explosion)
            self.root.after(1000, lambda: self.reveal_all_mines(r, c))
        else:
            # Pour les autres bombes, juste montrer l'explosion
            btn.config(text=explosion_stages[1], bg="red")

    def reveal_all_mines(self, clicked_r, clicked_c):
        """Révèle toutes les bombes avec un délai."""
        mines_to_reveal = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c]["mine"] and not (r == clicked_r and c == clicked_c):
                    mines_to_reveal.append((r, c))
        
        # Révéler les mines une par une avec un délai
        def reveal_next_mine(index=0):
            if index < len(mines_to_reveal):
                r, c = mines_to_reveal[index]
                self.animate_explosion(r, c)
                self.root.after(100, reveal_next_mine, index + 1)
            else:
                # Une fois toutes les mines révélées, terminer le jeu
                self.root.after(500, lambda: self.game_over(False))
        
        reveal_next_mine()

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

        if new_flag == 1:
            self.flags_count += 1
        elif new_flag == 2:
            self.question_marks_count += 1
        else:
            if current_flag == 1:
                self.flags_count -= 1
            elif current_flag == 2:
                self.question_marks_count -= 1
        
        self.update_flags()

    def update_flags(self):
        """Met à jour l'affichage des drapeaux et des points d'interrogation."""
        self.flags_label.config(text=f"Drapeaux: {self.flags_count}")
        self.questions_label.config(text=f"Points d'interrogation: {self.question_marks_count}")

    def check_win(self):
        """Vérifie si l'utilisateur a gagné."""
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.board[r][c]["revealed"] and not self.board[r][c]["mine"]:
                    return False
        return True

    def game_over(self, won):
        """Affiche le résultat et arrête le jeu."""
        self.running = False
        if won:
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.board[r][c]["mine"]:
                        self.board[r][c]["btn"].config(text="💣")
        # Désactiver tous les boutons et empêcher les clics
        self.disable_all_interactions()
        
        message = "Victoire ! 🎉" if won else "Perdu... 💥"
        self.timer_label.config(text=message)

    def update_timer(self):
        """Met à jour le chronomètre en temps réel."""
        if self.running:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Temps: {elapsed_time}s")
            self.root.after(1000, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    game = Demineur(root)
    root.mainloop()
