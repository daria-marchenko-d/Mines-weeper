import pygame
from game import Minesweeper

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    
    game = Minesweeper()
    game.run()