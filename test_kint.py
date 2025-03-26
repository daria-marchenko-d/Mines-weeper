import tkinter as tk
import random
import time

class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper")
        self.difficulty = {
            "Easy": (9, 9, 10),
            "Medium": (16, 16, 40),
            "Hard": (16, 30, 99)
        }
        self.start_time = None
        self.is_running = False

        self.first_click = True
        self.board = []
        self.flag_count = 0
        self.question_mark_count = 0
        self.total_flag_count = 0

        self.create_menu()

    def create_menu(self):
        """Creates the menu for selecting the difficulty level."""
        if hasattr(self, "game_frame"):
            self.game_frame.destroy()  # Destroy the game screen if it exists

        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.menu_frame, text="Choose difficulty level:").pack(pady=20)
        for level in self.difficulty:
            tk.Button(self.menu_frame, text=level, command=lambda level=level: self.start_game(level)).pack(pady=10)

    def start_game(self, level):
        """Starts a new game with the selected difficulty level."""
        self.level = level
        self.rows, self.columns, self.total_mines = self.difficulty[level]
        self.total_flag_count = self.total_mines

        self.first_click = True
        self.board = [[None for _ in range(self.columns)] for _ in range(self.rows)]
        self.flag_count = 0
        self.question_mark_count = 0

        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        if hasattr(self, "game_frame"):
            self.game_frame.destroy()

        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        # Timer label
        self.timer_label = tk.Label(self.game_frame, text="Time: 0s")
        self.timer_label.grid(row=0, column=0, columnspan=self.columns, sticky="nsew")

        self.mines_label = tk.Label(self.game_frame, text=f"Mines: {self.total_mines}", anchor="center")
        self.mines_label.grid(row=1, column=0, sticky="nsew")

        self.flags_label = tk.Label(self.game_frame, text=f"Flags: {self.total_flag_count}", anchor="center")
        self.flags_label.grid(row=1, column=1, sticky="nsew")

        self.questions_label = tk.Label(self.game_frame, text="Questions: 0", anchor="center")
        self.questions_label.grid(row=1, column=2, sticky="nsew")

        self.restart_button = tk.Button(self.game_frame, text="Restart", command=lambda: self.start_game(self.level))
        self.restart_button.grid(row=0, column=self.columns - 1, sticky="nsew")

        self.board_frame = tk.Frame(self.game_frame)
        self.board_frame.grid(row=2, column=0, columnspan=self.columns, sticky="nsew")

        # Create buttons for the grid
        for row_index in range(self.rows):
            for column_index in range(self.columns):
                cell_button = tk.Button(self.board_frame, width=3, height=2, command=lambda r=row_index, c=column_index: self.reveal_cell(r, c))
                cell_button.bind("<Button-3>", lambda event, r=row_index, c=column_index: self.toggle_flag(r, c))
                cell_button.grid(row=row_index, column=column_index, sticky="nsew")
                self.board[row_index][column_index] = {"button": cell_button, "is_mine": False, "is_revealed": False, "flag_status": 0}

        self.back_button = tk.Button(self.game_frame, text="Back", command=self.create_menu)
        self.back_button.grid(row=3, column=0, columnspan=self.columns, sticky="nsew")

        self.update_timer()

    def place_mines(self, safe_row, safe_column):
        """Places mines after the first click."""
        available_positions = [(row_index, column_index) for row_index in range(self.rows) for column_index in range(self.columns) if (row_index, column_index) != (safe_row, safe_column)]
        self.mines_positions = set(random.sample(available_positions, self.total_mines))

        for row_index, column_index in self.mines_positions:
            self.board[row_index][column_index]["is_mine"] = True

    def reveal_cell(self, row_index, column_index):
        """Reveals the cell and applies game rules."""
        if self.first_click:
            self.place_mines(row_index, column_index)
            self.first_click = False
            self.start_time = time.time()
            self.is_running = True

        if self.board[row_index][column_index]["is_revealed"] or self.board[row_index][column_index]["flag_status"] > 0:
            return

        self.board[row_index][column_index]["is_revealed"] = True
        self.board[row_index][column_index]["button"].config(relief=tk.SUNKEN)

        if self.board[row_index][column_index]["is_mine"]:
            self.board[row_index][column_index]["button"].config(text="💣", bg="red")
            self.end_game(False)
            return

        adjacent_mines_count = self.count_adjacent_mines(row_index, column_index)
        if adjacent_mines_count > 0:
            self.board[row_index][column_index]["button"].config(text=str(adjacent_mines_count))
        else:
            self.reveal_adjacent_cells(row_index, column_index)

        if self.check_win_condition():
            self.end_game(True)

    def count_adjacent_mines(self, row_index, column_index):
        """Counts the number of adjacent mines."""
        adjacent_mines_count = 0
        for row_offset in [-1, 0, 1]:
            for column_offset in [-1, 0, 1]:
                if (row_offset == 0 and column_offset == 0) or not (0 <= row_index + row_offset < self.rows and 0 <= column_index + column_offset < self.columns):
                    continue
                if self.board[row_index + row_offset][column_index + column_offset]["is_mine"]:
                    adjacent_mines_count += 1
        return adjacent_mines_count

    def reveal_adjacent_cells(self, row_index, column_index):
        """Reveals adjacent empty cells (recursion)."""
        for row_offset in [-1, 0, 1]:
            for column_offset in [-1, 0, 1]:
                adjacent_row = row_index + row_offset
                adjacent_column = column_index + column_offset
                if 0 <= adjacent_row < self.rows and 0 <= adjacent_column < self.columns and not self.board[adjacent_row][adjacent_column]["is_revealed"]:
                    self.reveal_cell(adjacent_row, adjacent_column)

    def toggle_flag(self, row_index, column_index):
        """Adds or removes a flag or question mark on the cell."""
        if self.board[row_index][column_index]["is_revealed"]:
            return

        current_flag_status = self.board[row_index][column_index]["flag_status"]
        new_flag_status = (current_flag_status + 1) % 3
        self.board[row_index][column_index]["flag_status"] = new_flag_status

        flag_symbols = ["", "🚩", "?"]
        self.board[row_index][column_index]["button"].config(text=flag_symbols[new_flag_status])

        if current_flag_status == 0 and new_flag_status == 1:
            self.flag_count += 1
            self.total_flag_count -= 1
        elif current_flag_status == 1 and new_flag_status == 2:
            self.flag_count -= 1
            self.question_mark_count += 1
            self.total_flag_count += 1
        elif current_flag_status == 2 and new_flag_status == 0:
            self.question_mark_count -= 1
            self.total_flag_count += 1

        self.update_labels()

    def check_win_condition(self):
        """Checks if all non-mine cells are revealed."""
        for row_index in range(self.rows):
            for column_index in range(self.columns):
                if not self.board[row_index][column_index]["is_mine"] and not self.board[row_index][column_index]["is_revealed"]:
                    return False
        return True

    def end_game(self, won):
        """Displays the result of the game and ends it."""
        self.is_running = False
        for row_index in range(self.rows):
            for column_index in range(self.columns):
                if self.board[row_index][column_index]["is_mine"]:
                    self.board[row_index][column_index]["button"].config(text="💣")
                self.board[row_index][column_index]["button"].config(state=tk.DISABLED)

        result_message = "You Win! 🎉" if won else "Game Over... 💥"
        self.timer_label.config(text=result_message)

    def update_timer(self):
        """Updates the timer."""
        if self.is_running and self.start_time:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {elapsed_time}s")
        self.root.after(1000, self.update_timer)

    def update_labels(self):
        """Updates the flag and question count labels."""
        self.flags_label.config(text=f"Flags left: {self.total_flag_count}")
        self.questions_label.config(text=f"Questions: {self.question_mark_count}")

root = tk.Tk()
game = Minesweeper(root)
root.mainloop()











