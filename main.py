import pygame

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

SCREEN_SIZE = 800


def draw_board(board_size):
    pygame.init()
    pygame.display.set_caption("Warcaby")
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    square_size = SCREEN_SIZE / board_size
    BACKGROUND_COLORS = [(230, 210, 170), (170, 120, 90)]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

            elif event.type == QUIT:
                running = False

        for row in range(board_size):
            color_index = row % 2
            for column in range(board_size):
                square = (
                    column * square_size,
                    row * square_size,
                    square_size,
                    square_size,
                )
                screen.fill(BACKGROUND_COLORS[color_index], square)
                color_index = (color_index + 1) % 2
        pygame.display.flip()


if __name__ == "__main__":
    draw_board(8)
