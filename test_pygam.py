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
    1: BLUE,
    2: GREEN,
    3: RED,
    4: (0, 0, 128),
    5: (128, 0, 0),
    6: (0, 128, 128),
    7: BLACK,
    8: GRAY
}

class Button:
    def __init__(self, x, y, width, height, text="", color=GRAY, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.is_hovered = False
        self.is_pressed = False
        self.font = pygame.font.SysFont('Arial', 20)
        
    def draw(self, surface):
        color = DARK_GRAY if self.is_pressed else (GRAY if self.is_hovered else self.color)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_pressed = False
        return False

class Cell:
    def __init__(self, x, y, size, font):
        self.rect = pygame.Rect(x, y, size, size)
        self.is_mine = False
        self.is_revealed = False
        self.flag_status = 0  # 0: none, 1: flag, 2: question
        self.adjacent_mines = 0
        self.font = font
        
    def draw(self, surface):
        if self.is_revealed:
            pygame.draw.rect(surface, WHITE, self.rect)
            pygame.draw.rect(surface, BLACK, self.rect, 1)
            
            if self.is_mine:
                text_surface = self.font.render("*", True, RED)
                text_rect = text_surface.get_rect(center=self.rect.center)
                surface.blit(text_surface, text_rect)
            elif self.adjacent_mines > 0:
                text_surface = self.font.render(str(self.adjacent_mines), True, COLORS[self.adjacent_mines])
                text_rect = text_surface.get_rect(center=self.rect.center)
                surface.blit(text_surface, text_rect)
        else:
            pygame.draw.rect(surface, GRAY, self.rect)
            pygame.draw.rect(surface, BLACK, self.rect, 1)
            
            if self.flag_status == 1:
                text_surface = self.font.render("F", True, GREEN)
                text_rect = text_surface.get_rect(center=self.rect.center)
                surface.blit(text_surface, text_rect)
            elif self.flag_status == 2:
                text_surface = self.font.render("?", True, BLACK)
                text_rect = text_surface.get_rect(center=self.rect.center)
                surface.blit(text_surface, text_rect)

class Minesweeper:
    def __init__(self):
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Minesweeper")
        
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 20)
        self.cell_font = pygame.font.SysFont('Arial', 16)
        
        self.difficulty = {
            "Easy": (9, 9, 10),
            "Medium": (16, 16, 40),
            "Hard": (16, 30, 99)
        }
        
        self.menu_buttons = []
        self.game_buttons = []
        self.cells = []
        self.state = "menu"
        self.create_menu()
        
        self.start_time = None
        self.is_running = False
        self.first_click = True
        self.flag_count = 0
        self.question_mark_count = 0
        self.total_flag_count = 0
        
    def calculate_cell_size(self):
        max_cell_width = (self.screen_width - 40) // self.columns
        max_cell_height = (self.screen_height - 150) // self.rows
        return min(max_cell_width, max_cell_height, 40)  # Максимальний розмір 40px

    def create_menu(self):
        self.menu_buttons = []
        self.state = "menu"
        
        title = self.font.render("Choose difficulty level:", True, BLACK)
        title_rect = title.get_rect(center=(self.screen_width//2, 100))
        
        button_width = 200
        button_height = 50
        start_y = 150
        spacing = 20
        
        for i, level in enumerate(self.difficulty):
            button = Button(
                self.screen_width//2 - button_width//2,
                start_y + i*(button_height + spacing),
                button_width,
                button_height,
                level
            )
            self.menu_buttons.append((button, level))
            
        self.back_button = None
        self.restart_button = None
        
    def start_game(self, level):
        self.level = level
        self.rows, self.columns, self.total_mines = self.difficulty[level]
        self.total_flag_count = self.total_mines
        
        self.first_click = True
        self.flag_count = 0
        self.question_mark_count = 0
        self.state = "game"
        
        # Автоматичний розрахунок розміру клітинки
        self.cell_size = self.calculate_cell_size()
        
        # Розрахунок позиції ігрового поля
        board_width = self.columns * self.cell_size
        board_height = self.rows * self.cell_size
        self.board_x = (self.screen_width - board_width) // 2
        self.board_y = 100
        
        # Створення клітинок
        self.cells = []
        for row in range(self.rows):
            for col in range(self.columns):
                x = self.board_x + col * self.cell_size
                y = self.board_y + row * self.cell_size
                self.cells.append(Cell(x, y, self.cell_size, self.cell_font))
                
        # Кнопки гри
        self.game_buttons = []
        self.restart_button = Button(
            self.screen_width - 120,
            20,
            100,
            40,
            "Restart"
        )
        
        self.back_button = Button(
            20,
            20,
            100,
            40,
            "Back"
        )
        
    def place_mines(self, safe_row, safe_col):
        safe_index = safe_row * self.columns + safe_col
        available_positions = [i for i in range(len(self.cells)) if i != safe_index]
        self.mines_positions = random.sample(available_positions, self.total_mines)
        
        for index in self.mines_positions:
            self.cells[index].is_mine = True
            
        for i, cell in enumerate(self.cells):
            if not cell.is_mine:
                row = i // self.columns
                col = i % self.columns
                cell.adjacent_mines = self.count_adjacent_mines(row, col)
                
    def count_adjacent_mines(self, row, col):
        count = 0
        for r in [-1, 0, 1]:
            for c in [-1, 0, 1]:
                if r == 0 and c == 0:
                    continue
                new_row, new_col = row + r, col + c
                if 0 <= new_row < self.rows and 0 <= new_col < self.columns:
                    index = new_row * self.columns + new_col
                    if self.cells[index].is_mine:
                        count += 1
        return count
    
    def reveal_cell(self, row, col):
        index = row * self.columns + col
        cell = self.cells[index]
        
        if cell.is_revealed or cell.flag_status > 0:
            return
            
        if self.first_click:
            self.place_mines(row, col)
            self.first_click = False
            self.start_time = time.time()
            self.is_running = True
            
        cell.is_revealed = True
        
        if cell.is_mine:
            self.end_game(False)
            return
            
        if cell.adjacent_mines == 0:
            self.reveal_adjacent_cells(row, col)
            
        if self.check_win_condition():
            self.end_game(True)
            
    def reveal_adjacent_cells(self, row, col):
        for r in [-1, 0, 1]:
            for c in [-1, 0, 1]:
                if r == 0 and c == 0:
                    continue
                new_row, new_col = row + r, col + c
                if 0 <= new_row < self.rows and 0 <= new_col < self.columns:
                    index = new_row * self.columns + new_col
                    if not self.cells[index].is_revealed and not self.cells[index].is_mine:
                        self.reveal_cell(new_row, new_col)
    
    def toggle_flag(self, row, col):
        index = row * self.columns + col
        cell = self.cells[index]
        
        if cell.is_revealed:
            return
            
        current_flag_status = cell.flag_status
        new_flag_status = (current_flag_status + 1) % 3
        cell.flag_status = new_flag_status
        
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
    
    def check_win_condition(self):
        for cell in self.cells:
            if not cell.is_mine and not cell.is_revealed:
                return False
        return True
        
    def end_game(self, won):
        self.is_running = False
        self.state = "game_over"
        self.game_over_won = won
        
        for cell in self.cells:
            if cell.is_mine:
                cell.is_revealed = True
    
    def update_timer(self):
        if self.is_running and self.start_time:
            self.elapsed_time = int(time.time() - self.start_time)
    
    def draw_menu(self):
        self.screen.fill(WHITE)
        
        title = self.font.render("Choose difficulty level:", True, BLACK)
        title_rect = title.get_rect(center=(self.screen_width//2, 50))
        self.screen.blit(title, title_rect)
        
        for button, _ in self.menu_buttons:
            button.draw(self.screen)
            
        pygame.display.flip()
    
    def draw_game(self):
        self.screen.fill(WHITE)
        
        if self.is_running:
            self.update_timer()
            timer_text = f"Time: {self.elapsed_time}s"
        else:
            timer_text = "Time: 0s"
            
        timer_surface = self.font.render(timer_text, True, BLACK)
        self.screen.blit(timer_surface, (20, 60))
        
        mines_text = f"Mines: {self.total_mines}"
        mines_surface = self.font.render(mines_text, True, BLACK)
        self.screen.blit(mines_surface, (self.screen_width//2 - 50, 60))
        
        flags_text = f"Flags: {self.total_flag_count}"
        flags_surface = self.font.render(flags_text, True, BLACK)
        self.screen.blit(flags_surface, (self.screen_width - 150, 60))
        
        self.restart_button.draw(self.screen)
        self.back_button.draw(self.screen)
        
        for cell in self.cells:
            cell.draw(self.screen)
            
        if self.state == "game_over":
            message = "You Win! 🎉" if self.game_over_won else "Game Over... 💥"
            message_surface = self.font.render(message, True, RED)
            message_rect = message_surface.get_rect(center=(self.screen_width//2, 40))
            self.screen.blit(message_surface, message_rect)
            
        pygame.display.flip()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if self.state == "menu":
                for button, level in self.menu_buttons:
                    if button.handle_event(event):
                        self.start_game(level)
                        
            elif self.state in ["game", "game_over"]:
                if self.restart_button.handle_event(event):
                    self.start_game(self.level)
                    
                if self.back_button.handle_event(event):
                    self.create_menu()
                    
                if event.type == pygame.MOUSEBUTTONDOWN and self.state == "game":
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if (self.board_x <= mouse_pos[0] < self.board_x + self.columns * self.cell_size and
                        self.board_y <= mouse_pos[1] < self.board_y + self.rows * self.cell_size):
                        
                        col = (mouse_pos[0] - self.board_x) // self.cell_size
                        row = (mouse_pos[1] - self.board_y) // self.cell_size
                        
                        if event.button == 1:
                            self.reveal_cell(row, col)
                        elif event.button == 3:
                            self.toggle_flag(row, col)
    
    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.handle_events()
            
            if self.state == "menu":
                self.draw_menu()
            elif self.state in ["game", "game_over"]:
                self.draw_game()
                
            clock.tick(60)

if __name__ == "__main__":
    game = Minesweeper()
    game.run()














