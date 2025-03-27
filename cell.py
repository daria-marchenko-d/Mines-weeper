import pygame
from constants import *

class Cell:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.is_mine = False
        self.is_revealed = False
        self.flag_status = 0  # 0: none, 1: flag, 2: question
        self.adjacent_mines = 0
        
    def draw(self, surface, font, bomb_image, flag_image):
        color = WHITE if self.is_revealed else GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 1)
        
        if self.is_revealed:
            if self.is_mine:
                bomb_offset = (self.rect.width - bomb_image.get_width()) // 2
                surface.blit(bomb_image, (self.rect.x + bomb_offset, self.rect.y + bomb_offset))
            elif self.adjacent_mines > 0:
                text = font.render(str(self.adjacent_mines), True, COLORS[self.adjacent_mines])
                surface.blit(text, text.get_rect(center=self.rect.center))
        elif self.flag_status == 1:
            flag_offset = (self.rect.width - flag_image.get_width()) // 2
            surface.blit(flag_image, (self.rect.x + flag_offset, self.rect.y + flag_offset))
        elif self.flag_status == 2:
            text = font.render("?", True, BLACK)
            surface.blit(text, text.get_rect(center=self.rect.center))
            