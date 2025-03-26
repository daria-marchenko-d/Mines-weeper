import tkinter as tk
import random
import time


class MinesweeperGame:
    def __init__(self, root):
        """Initialize the Minesweeper game window."""
        self.root = root
        self.root.title("Minesweeper")

        # Difficulty settings: (rows, columns, number_of_mines)
        self.difficulty_levels = {
            "Easy": (9, 9, 10),
            "Medium": (16, 16, 40),
            "Hard": (16, 30, 99)
        }

        self.start_time = None  # To track game time
        self.game_running = False

        # Initialize game attributes
        self.first_click = True  # Ensures first click is never a mine
        self.game_board = []
        self.flag_count = 0
        self.question_mark_count = 0

        self.create_menu()

    def create_menu(self):
        """Create the main menu where the player selects difficulty level."""
        if hasattr(self, "game_frame"):
            self.game_frame.destroy()  # Remove the game board if it exists

        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.menu_frame, text="Select Difficulty:").pack(pady=20)

        # Create difficulty buttons
        for level in self.difficulty_levels:
            tk.Button(self.menu_frame, text=level, command=lambda l=level: self.start_new_game(l)).pack(pady=10)

    def start_new_game(self, level):
        """Start a new game with the selected difficulty."""
        self.current_level = level
        self.rows, self.columns, self.number_of_mines = self.difficulty_levels[level]

        # Reset game attributes
        self.first_click = True
        self.game_board = [[None for _ in range(self.columns)] for _ in range(self.rows)]
        self.flag_count = 0
        self.question_mark_count = 0

        # Destroy previous UI elements
        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        if hasattr(self, "game_frame"):
            self.game_frame.destroy()

        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        # Timer label
        self.timer_label = tk.Label(self.game_frame, text="Time: 0s")
        self.timer_label.grid(row=0, column=0, columnspan=self.columns, sticky="nsew")

        # Labels for mines, flags, and question marks
        self.mines_label = tk.Label(self.game_frame, text=f"Mines: {self.number_of_mines}")
        self.mines_label.grid(row=1, column=0, sticky="nsew")

        self.flags_label = tk.Label(self.game_frame, text="Flags: 0")
        self.flags_label.grid(row=1, column=1, sticky="nsew")

        self.question_marks_label = tk.Label(self.game_frame, text="Question Marks: 0")
        self.question_marks_label.grid(row=1, column=2, sticky="nsew")

        # Restart button
        self.restart_button = tk.Button(self.game_frame, text="Restart", command=lambda: self.start_new_game(self.current_level))
        self.restart_button.grid(row=0, column=self.columns - 1, sticky="nsew")

        # Board frame where the buttons (cells) will be placed
        self.board_frame = tk.Frame(self.game_frame)
        self.board_frame.grid(row=2, column=0, columnspan=self.columns, sticky="nsew")

        # Create buttons for each cell
        for row in range(self.rows):
            for column in range(self.columns):
                cell_button = tk.Button(self.board_frame, width=2, height=1, command=lambda r=row, c=column: self.reveal_cell(r, c))
                cell_button.bind("<Button-3>", lambda event, r=row, c=column: self.toggle_flag(r, c))
                cell_button.grid(row=row, column=column, sticky="nsew")
                self.game_board[row][column] = {"button": cell_button, "mine": False, "revealed": False, "flag": 0}

        # Back to menu button
        self.back_button = tk.Button(self.game_frame, text="Back to Menu", command=self.create_menu)
        self.back_button.grid(row=3, column=0, columnspan=self.columns, sticky="nsew")

        self.update_timer()

    def place_mines(self, safe_row, safe_column):
        """Randomly place mines on the board, ensuring the first click is safe."""
        available_positions = [(r, c) for r in range(self.rows) for c in range(self.columns) if (r, c) != (safe_row, safe_column)]
        self.mines_positions = set(random.sample(available_positions, self.number_of_mines))

        for row, column in self.mines_positions:
            self.game_board[row][column]["mine"] = True

    def reveal_cell(self, row, column):
        """Reveal a cell and apply the game rules."""
        if self.first_click:
            self.place_mines(row, column)
            self.first_click = False
            self.start_time = time.time()
            self.game_running = True

        if self.game_board[row][column]["revealed"] or self.game_board[row][column]["flag"] > 0:
            return

        self.game_board[row][column]["revealed"] = True
        self.game_board[row][column]["button"].config(relief=tk.SUNKEN)

        if self.game_board[row][column]["mine"]:
            self.game_board[row][column]["button"].config(text="💣", bg="red")
            self.end_game(False)
            return

        adjacent_mines = self.count_adjacent_mines(row, column)
        if adjacent_mines > 0:
            self.game_board[row][column]["button"].config(text=str(adjacent_mines))
        else:
            self.reveal_adjacent_cells(row, column)

        if self.check_win():
            self.end_game(True)

    def count_adjacent_mines(self, row, column):
        """Count the number of mines adjacent to a given cell."""
        count = 0
        for row_offset in [-1, 0, 1]:
            for column_offset in [-1, 0, 1]:
                if (row_offset == 0 and column_offset == 0) or not (0 <= row+row_offset < self.rows and 0 <= column+column_offset < self.columns):
                    continue
                if self.game_board[row+row_offset][column+column_offset]["mine"]:
                    count += 1
        return count

    def reveal_adjacent_cells(self, row, column):
        """Recursively reveal adjacent empty cells."""
        for row_offset in [-1, 0, 1]:
            for column_offset in [-1, 0, 1]:
                new_row, new_column = row + row_offset, column + column_offset
                if 0 <= new_row < self.rows and 0 <= new_column < self.columns and not self.game_board[new_row][new_column]["revealed"]:
                    self.reveal_cell(new_row, new_column)

    def toggle_flag(self, row, column):
        """Cycle through flag states (empty → flag → question mark → empty)."""
        if self.game_board[row][column]["revealed"]:
            return

        flag_states = ["", "🚩", "?"]
        self.game_board[row][column]["flag"] = (self.game_board[row][column]["flag"] + 1) % 3
        self.game_board[row][column]["button"].config(text=flag_states[self.game_board[row][column]["flag"]])

    def check_win(self):
        """Check if all non-mine cells have been revealed."""
        return all(cell["revealed"] or cell["mine"] for row in self.game_board for cell in row)

    def end_game(self, won):
        """Display the game result and disable further actions."""
        self.game_running = False
        for row in self.game_board:
            for cell in row:
                if cell["mine"]:
                    cell["button"].config(text="💣")
                cell["button"].config(state=tk.DISABLED)

        self.timer_label.config(text="Victory! 🎉" if won else "Game Over 💥")

    def update_timer(self):
        """Update the game timer."""
        if self.game_running and self.start_time:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {elapsed_time}s")
        self.root.after(1000, self.update_timer)


if __name__ == "__main__":
    root = tk.Tk()
    game = MinesweeperGame(root)
    root.mainloop()


