import pygame

from board import Board

SCREEN_SIZE = 800


def main():
    """
    Main function of the game
    """
    pygame.init()
    pygame.display.set_caption("Warcaby")
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))

    board_size = 8
    pawns_rows = 2
    board = Board(screen, board_size, pawns_rows)
    board.draw_board()


if __name__ == "__main__":
    main()
