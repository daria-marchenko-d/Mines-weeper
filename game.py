import pygame
import random
import time
import sys
from button import Button
from cell import Cell
from constants import *
from database import Database

class Minesweeper:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Minesweeper")

        # Load assets
        self.background = pygame.image.load("images/backgr.jpg")
        self.background = pygame.transform.scale(self.background, self.screen.get_size())
        self.music = pygame.mixer.music.load("sounds/background.mp3")
        self.fail_sound = pygame.mixer.Sound("sounds/failfare.mp3")
        self.click_sound = pygame.mixer.Sound("sounds/click.mp3")
        self.explosion_sound = pygame.mixer.Sound("sounds/explosion.mp3")
        self.win_sound = pygame.mixer.Sound("sounds/fanfare.mp3")
        pygame.mixer.music.play(-1)
        
        # Fonts
        self.large_font = pygame.font.SysFont('Arial', 24)
        self.medium_font = pygame.font.SysFont('Arial', 20)
        self.cell_font = pygame.font.SysFont('Arial', 16)
        
        # Images
        self.original_bomb_image = pygame.image.load("images/bomb.png")
        self.original_flag_image = pygame.image.load("images/flag.png")
        self.bomb_image = None
        self.flag_image = None
        
        # Database
        self.db = Database()
        self.player_name = ""
        self.name_input = ""
        self.name_input_active = False
        self.show_scores = False
        
        # Initialize game state
        self.initialize_game()

    def initialize_game(self):
        self.cells = []
        self.game_state = "menu"
        self.first_click = True
        self.game_running = False
        self.start_time = None
        self.victory = False
        self.remaining_flags = 0
        self.total_mines = 0
        self.current_level = "Easy"
        self.mines_to_reveal = []
        self.current_mine_index = 0
        
        # Menu buttons
        self.menu_buttons = [
            Button(300, 150 + index*70, 200, 50, level_name) 
            for index, level_name in enumerate(DIFFICULTY_LEVELS)
        ]
        self.score_buttons = [
            Button(300, 550, 200, 40, "Go back"),
            Button(300, 600, 200, 40, "Delete last player")
        ]
        self.restart_button = Button(550, 60, 100, 40, "Restart")
        self.menu_button = Button(50, 60, 100, 40, "Menu")

    def start_game(self, level_name):
        if level_name not in DIFFICULTY_LEVELS:
            level_name = "Easy"
            
        level = DIFFICULTY_LEVELS[level_name]
        self.rows = level["rows"]
        self.columns = level["columns"]
        self.total_mines = level["mines"]
        self.remaining_flags = self.total_mines
        self.current_level = level_name
        
        # Calculate cell size
        max_cell_width = (SCREEN_WIDTH - 40) // self.columns
        max_cell_height = (SCREEN_HEIGHT - 200) // self.rows
        self.cell_size = min(max_cell_width, max_cell_height, 40)
        
        # Scale images
        bomb_size = int(self.cell_size * 0.7)
        flag_size = int(self.cell_size * 0.8)
        self.bomb_image = pygame.transform.scale(self.original_bomb_image, (bomb_size, bomb_size))
        self.flag_image = pygame.transform.scale(self.original_flag_image, (flag_size, flag_size))
        
        # Create board
        board_width = self.columns * self.cell_size
        board_height = self.rows * self.cell_size
        self.board_x_position = (SCREEN_WIDTH - board_width) // 2
        self.board_y_position = 150
        
        # Initialize cells
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
        self.first_click = True
        self.game_running = False
        self.victory = False

    def place_mines(self, safe_row, safe_column):
        safe_index = safe_row * self.columns + safe_column
        possible_positions = [
            index for index in range(len(self.cells)) 
            if index != safe_index
        ]
        
        for mine_index in random.sample(possible_positions, self.total_mines):
            self.cells[mine_index].is_mine = True
            
        # Calculate adjacent mines
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
        if not (0 <= row < self.rows and 0 <= column < self.columns):
            return
            
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
            self.explosion_sound.play()
            self.fail_sound.play()
            self.end_game(False)
        elif cell.adjacent_mines == 0:
            self.reveal_adjacent_cells(row, column)
        
        if self.check_win_condition():
            self.win_sound.play()
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
        if not (0 <= row < self.rows and 0 <= column < self.columns):
            return
            
        cell_index = row * self.columns + column
        cell = self.cells[cell_index]
        
        if cell.is_revealed:
            return
            
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

    def save_game_result(self, time_elapsed, status):
        if self.player_name:
            player_id = self.db.add_player(self.player_name)
            self.db.add_score(
                player_id,
                time_elapsed,
                "Won" if status else "Lost",
                self.total_mines - self.remaining_flags,
                self.current_level
            )

    def end_game(self, victory):
        self.game_running = False
        self.game_state = "game_over"
        self.victory = victory
        
        if not victory:
            # Find clicked bomb
            clicked_row, clicked_col = -1, -1
            for i, cell in enumerate(self.cells):
                if cell.is_mine and cell.is_revealed:
                    clicked_row = i // self.columns
                    clicked_col = i % self.columns
                    break
            
            # Prepare mines for animation
            self.mines_to_reveal = [
                (row, col) 
                for row in range(self.rows) 
                for col in range(self.columns) 
                if self.cells[row * self.columns + col].is_mine 
                and not (row == clicked_row and col == clicked_col)
            ]
            self.current_mine_index = 0
            pygame.time.set_timer(pygame.USEREVENT, 100)
        else:
            for cell in self.cells:
                if cell.is_mine:
                    cell.is_revealed = True
        
        # Save game result
        time_elapsed = int(time.time() - self.start_time)
        self.save_game_result(time_elapsed, victory)

    def draw_name_input(self):
        pygame.draw.rect(self.screen, WHITE, (300, 500, 200, 40))
        pygame.draw.rect(self.screen, BLACK, (300, 500, 200, 40), 2)
        
        font = pygame.font.SysFont('Arial', 20)
        text_surface = font.render(self.name_input, True, BLACK)
        self.screen.blit(text_surface, (310, 510))
        
        prompt = font.render("Enter your name:", True, WHITE)
        self.screen.blit(prompt, (300, 470))

    def draw_scores(self):
        pygame.draw.rect(self.screen, LIGHT_VIOLET, (30, 135, 750, 400))
        pygame.draw.rect(self.screen, BLACK, (30, 135, 750, 400), 2)
        
        font = pygame.font.SysFont('Arial', 20)
        title = font.render("Game History", True, WHITE)
        self.screen.blit(title, (350, 150))
        
        headers = ["Name", "Time", "Status", "Flags", "Difficulty", "Date"]
        for i, header in enumerate(headers):
            text = font.render(header, True, WHITE)
            self.screen.blit(text, (50 + i*110, 220))
        
        scores = self.db.get_scores()
        for i, score in enumerate(scores[:5]):
            for j, item in enumerate(score):
                text = font.render(str(item), True, WHITE)
                self.screen.blit(text, (50 + j*110, 260 + i*30))
        
        # Control buttons
        for button in self.score_buttons:
            button.draw(self.screen)

    def draw_info_panel(self):
        pygame.draw.rect(self.screen, VIOLET, (0, 0, SCREEN_WIDTH, 80))
        
        timer_text = f"Time: {int(time.time() - self.start_time)}s" if self.game_running else "Time: 0s"
        self.screen.blit(self.large_font.render(timer_text, True, WHITE), (50, 30))
        
        mines_text = f"Mines: {self.total_mines}"
        self.screen.blit(self.large_font.render(mines_text, True, WHITE), (300, 30))
        
        flags_text = f"Flags: {self.remaining_flags}"
        self.screen.blit(self.large_font.render(flags_text, True, WHITE), (550, 30))

    def draw_menu(self):
        self.screen.fill(VIOLET)
        self.screen.blit(self.background, (0, 0))
        
        if not self.player_name:
            self.draw_name_input()
        else:
            title = self.large_font.render(f"Player: {self.player_name}", True, WHITE)
            self.screen.blit(title, (300, 100))
            
            if self.show_scores:
                self.draw_scores()
            else:
                for button in self.menu_buttons:
                    button.draw(self.screen)
                
                score_button = Button(300, 400, 200, 50, "Show Scores")
                score_button.draw(self.screen)

    def draw_game(self):
        self.screen.fill(VIOLET)
        self.draw_info_panel()
        self.restart_button.draw(self.screen)
        self.menu_button.draw(self.screen)
        
        for cell in self.cells:
            cell.draw(self.screen, self.cell_font, self.bomb_image, self.flag_image)
        
        if self.game_state == "game_over":
            result_text = "You Win!" if self.victory else "Game Over!"
            self.screen.blit(self.large_font.render(result_text, True, RED), (350, 100))

    def handle_name_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.name_input:
                    self.player_name = self.name_input
                    self.db.add_player(self.player_name)
                    self.name_input_active = False
            elif event.key == pygame.K_BACKSPACE:
                self.name_input = self.name_input[:-1]
            else:
                self.name_input += event.unicode

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.db.close()
                pygame.quit()
                sys.exit()
                
            if self.name_input_active:
                self.handle_name_input(event)
            else:
                if event.type == pygame.USEREVENT and hasattr(self, 'mines_to_reveal'):
                    if self.current_mine_index < len(self.mines_to_reveal):
                        row, col = self.mines_to_reveal[self.current_mine_index]
                        cell_index = row * self.columns + col
                        if 0 <= cell_index < len(self.cells):
                            self.cells[cell_index].is_revealed = True
                        self.current_mine_index += 1
                    else:
                        pygame.time.set_timer(pygame.USEREVENT, 0)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self.click_sound.play()
                    
                    if not self.player_name:
                        if 300 <= mouse_pos[0] <= 500 and 500 <= mouse_pos[1] <= 540:
                            self.name_input_active = True
                    
                    elif self.show_scores:
                        for i, button in enumerate(self.score_buttons):
                            if button.is_clicked(mouse_pos):
                                if i == 0:  # Show Scores
                                    self.show_scores = False
                                elif i == 1:  # Delete Data
                                    player_id = self.db.add_player(self.player_name)
                                    self.db.delete_player_data(player_id)
                                    self.player_name = ""
                                    self.show_scores = False
                    
                    elif self.game_state == "menu":
                        for button in self.menu_buttons:
                            if button.is_clicked(mouse_pos):
                                self.start_game(button.text)
                        
                        if 300 <= mouse_pos[0] <= 500 and 400 <= mouse_pos[1] <= 450:
                            self.show_scores = True
                    
                    elif self.game_state in ["game", "game_over"]:
                        if self.restart_button.is_clicked(mouse_pos) and self.current_level:
                            self.start_game(self.current_level)
                        elif self.menu_button.is_clicked(mouse_pos):
                            self.initialize_game()
                        elif self.game_state == "game":
                            for cell_index, cell in enumerate(self.cells):
                                if cell.rect.collidepoint(mouse_pos):
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