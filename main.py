import pygame
from game import Minesweeper

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    
    game = Minesweeper()
    game.run()
# import pygame
# from game import Minesweeper

# if __name__ == "__main__":
#     pygame.init()
#     pygame.font.init()
    
#     try:
#         game = Minesweeper()
#         game.run()
#     finally:
#         pygame.quit()