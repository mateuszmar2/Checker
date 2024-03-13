import pygame

from board import Board

SCREEN_SIZE = 800


def main():
    pygame.init()
    pygame.display.set_caption("Warcaby")
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))

    board_size = 8
    board = Board(board_size)
    board.draw_board(screen)


if __name__ == "__main__":
    main()
