import pygame
import random
import time
import sys

# Ініціалізація pygame
pygame.init()
pygame.font.init()

# Кольори
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
COLORS = {
    1: BLUE, 2: GREEN, 3: RED, 4: (0, 0, 128),
    5: (128, 0, 0), 6: (0, 128, 128), 7: BLACK, 8: GRAY
}

class Button:
    def __init__(self, x, y, width, height, text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont('Arial', 20)
        
    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        if self.text:
            text_surface = self.font.render(self.text, True, BLACK)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

class Cell:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.is_mine = False
        self.is_revealed = False
        self.flag_status = 0  # 0: none, 1: flag, 2: question
        self.adjacent_mines = 0
        
    def draw(self, surface, font):
        color = WHITE if self.is_revealed else GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 1)
        
        if self.is_revealed:
            if self.is_mine:
                text = font.render("*", True, RED)
                surface.blit(text, text.get_rect(center=self.rect.center))
            elif self.adjacent_mines > 0:
                text = font.render(str(self.adjacent_mines), True, COLORS[self.adjacent_mines])
                surface.blit(text, text.get_rect(center=self.rect.center))
        elif self.flag_status == 1:
            text = font.render("F", True, GREEN)
            surface.blit(text, text.get_rect(center=self.rect.center))
        elif self.flag_status == 2:
            text = font.render("?", True, BLACK)
            surface.blit(text, text.get_rect(center=self.rect.center))

class Minesweeper:
    def __init__(self):
        self.screen_width = 800
        self.screen_height = 650  # Збільшено для інформаційної панелі
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Minesweeper")
        
        self.large_font = pygame.font.SysFont('Arial', 24)
        self.medium_font = pygame.font.SysFont('Arial', 20)
        self.cell_font = pygame.font.SysFont('Arial', 16)
        
        self.difficulty_levels = {
            "Easy": {"rows": 9, "columns": 9, "mines": 10},
            "Medium": {"rows": 16, "columns": 16, "mines": 40},
            "Hard": {"rows": 16, "columns": 30, "mines": 99}
        }
        
        self.initialize_menu()
        
    def initialize_menu(self):
        self.cells = []
        self.game_state = "menu"
        self.menu_buttons = [
            Button(300, 150 + index*70, 200, 50, level_name) 
            for index, level_name in enumerate(self.difficulty_levels)
        ]
        
    def start_game(self, level_name):
        self.current_level = level_name
        level = self.difficulty_levels[level_name]
        self.rows = level["rows"]
        self.columns = level["columns"]
        self.total_mines = level["mines"]
        self.remaining_flags = self.total_mines
        self.first_click = True
        self.game_running = False
        self.start_time = None
        self.victory = False
        
        # Розрахунок розміру клітинок
        max_cell_width = (self.screen_width - 40) // self.columns
        max_cell_height = (self.screen_height - 200) // self.rows
        self.cell_size = min(max_cell_width, max_cell_height, 40)
        
        # Позиція ігрового поля
        board_width = self.columns * self.cell_size
        board_height = self.rows * self.cell_size
        self.board_x_position = (self.screen_width - board_width) // 2
        self.board_y_position = 150
        
        # Створення клітинок
        self.cells = [
            Cell(
                self.board_x_position + column * self.cell_size, 
                self.board_y_position + row * self.cell_size, 
                self.cell_size
            ) 
            for row in range(self.rows) 
            for column in range(self.columns)
        ]
        
        self.game_state = "game"
        self.restart_button = Button(650, 50, 100, 40, "Restart")
        self.menu_button = Button(50, 50, 100, 40, "Menu")

    def place_mines(self, safe_row, safe_column):
        safe_index = safe_row * self.columns + safe_column
        possible_positions = [
            index for index in range(len(self.cells)) 
            if index != safe_index
        ]
        
        for mine_index in random.sample(possible_positions, self.total_mines):
            self.cells[mine_index].is_mine = True
            
        for index, cell in enumerate(self.cells):
            if not cell.is_mine:
                row = index // self.columns
                column = index % self.columns
                cell.adjacent_mines = self.count_adjacent_mines(row, column)

    def count_adjacent_mines(self, row, column):
        count = 0
        for row_offset in [-1, 0, 1]:
            for column_offset in [-1, 0, 1]:
                if row_offset == 0 and column_offset == 0:
                    continue
                new_row = row + row_offset
                new_column = column + column_offset
                if 0 <= new_row < self.rows and 0 <= new_column < self.columns:
                    if self.cells[new_row * self.columns + new_column].is_mine:
                        count += 1
        return count
    
    def reveal_cell(self, row, column):
        cell_index = row * self.columns + column
        cell = self.cells[cell_index]
        
        if cell.is_revealed or cell.flag_status != 0:
            return
            
        if self.first_click:
            self.place_mines(row, column)
            self.first_click = False
            self.game_running = True
            self.start_time = time.time()
            
        cell.is_revealed = True
        
        if cell.is_mine:
            self.end_game(False)
        elif cell.adjacent_mines == 0:
            self.reveal_adjacent_cells(row, column)
        
        if self.check_win_condition():
            self.end_game(True)

    def reveal_adjacent_cells(self, row, column):
        for row_offset in [-1, 0, 1]:
            for column_offset in [-1, 0, 1]:
                if row_offset == 0 and column_offset == 0:
                    continue
                new_row = row + row_offset
                new_column = column + column_offset
                if 0 <= new_row < self.rows and 0 <= new_column < self.columns:
                    self.reveal_cell(new_row, new_column)

    def toggle_flag(self, row, column):
        cell_index = row * self.columns + column
        cell = self.cells[cell_index]
        
        if cell.is_revealed:
            return
            
        # Cycle through flag states: none → flag → question → none
        if cell.flag_status == 0 and self.remaining_flags > 0:
            cell.flag_status = 1
            self.remaining_flags -= 1
        elif cell.flag_status == 1:
            cell.flag_status = 2
            self.remaining_flags += 1
        elif cell.flag_status == 2:
            cell.flag_status = 0

    def check_win_condition(self):
        for cell in self.cells:
            if not cell.is_mine and not cell.is_revealed:
                return False
        return True

    def end_game(self, victory):
        self.game_running = False
        self.game_state = "game_over"
        self.victory = victory
        for cell in self.cells:
            if cell.is_mine:
                cell.is_revealed = True

    def draw_info_panel(self):
        # Панель інформації
        pygame.draw.rect(self.screen, WHITE, (0, 0, self.screen_width, 80))
        
        # Таймер
        timer_text = f"Time: {int(time.time() - self.start_time)}s" if self.game_running else "Time: 0s"
        self.screen.blit(self.large_font.render(timer_text, True, BLACK), (50, 30))
        
        # Кількість мін
        mines_text = f"Mines: {self.total_mines}"
        self.screen.blit(self.large_font.render(mines_text, True, BLACK), (300, 30))
        
        # Залишилось прапорців
        flags_text = f"Flags: {self.remaining_flags}"
        self.screen.blit(self.large_font.render(flags_text, True, BLACK), (550, 30))

    def draw_menu(self):
        self.screen.fill(WHITE)
        title = self.large_font.render("Select difficulty level:", True, BLACK)
        self.screen.blit(title, (300, 100))
        for button in self.menu_buttons:
            button.draw(self.screen)

    def draw_game(self):
        self.screen.fill(WHITE)
        
        # Інформаційна панель
        self.draw_info_panel()
        
        # Кнопки
        self.restart_button.draw(self.screen)
        self.menu_button.draw(self.screen)
        
        # Ігрове поле
        for cell in self.cells:
            cell.draw(self.screen, self.cell_font)
        
        # Результат гри
        if self.game_state == "game_over":
            result_text = "You Win!" if self.victory else "Game Over!"
            self.screen.blit(self.large_font.render(result_text, True, RED), (350, 100))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.mouse.get_pos()
                
                if self.game_state == "menu":
                    for button in self.menu_buttons:
                        if button.rect.collidepoint(mouse_position):
                            self.start_game(button.text)
                            
                elif self.game_state in ["game", "game_over"]:
                    if self.restart_button.rect.collidepoint(mouse_position):
                        self.start_game(self.current_level)
                    elif self.menu_button.rect.collidepoint(mouse_position):
                        self.initialize_menu()
                    elif self.game_state == "game":
                        for cell_index, cell in enumerate(self.cells):
                            if cell.rect.collidepoint(mouse_position):
                                row = cell_index // self.columns
                                column = cell_index % self.columns
                                if event.button == 1:  # Left click
                                    self.reveal_cell(row, column)
                                elif event.button == 3:  # Right click
                                    self.toggle_flag(row, column)

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.handle_events()
            
            if self.game_state == "menu":
                self.draw_menu()
            else:
                self.draw_game()
            
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    game = Minesweeper()
    game.run()