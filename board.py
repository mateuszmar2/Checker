import pygame
from enum import Enum

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)


class Pawns(Enum):
    BLACK_PAWN = {"index": 1, "color": (0, 0, 0)}
    WHITE_PAWN = {"index": 2, "color": (255, 255, 255)}


class Board:
    white_pawns = []
    black_pawns = []
    size = 0

    def __init__(self, size):
        self.size = size

        for column in range(size):
            for row in range(2):
                if (row + column) % 2 == 1:
                    self.black_pawns.append((row, column))

            for row in range(size - 2, size):
                if (row + column) % 2 == 1:
                    self.white_pawns.append((row, column))

    def draw_pawn(self, screen, square_size, row, column, pawn):
        pawn_radius = square_size // 3
        pawn_x = column * square_size + square_size // 2
        pawn_y = row * square_size + square_size // 2
        pygame.draw.circle(screen, pawn.value["color"], (pawn_x, pawn_y), pawn_radius)

    def draw_board(self, screen):
        BACKGROUND_COLORS = [(230, 210, 170), (170, 120, 90)]
        screen_size = screen.get_width()
        square_size = screen_size // self.size

        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False

                elif event.type == QUIT:
                    running = False

            # Draw the board
            for row in range(self.size):
                color_index = row % 2
                for column in range(self.size):
                    square = (
                        column * square_size,
                        row * square_size,
                        square_size,
                        square_size,
                    )
                    screen.fill(BACKGROUND_COLORS[color_index], square)
                    color_index = (color_index + 1) % 2

            # Draw the pawns
            for row, column in self.black_pawns:
                self.draw_pawn(screen, square_size, row, column, Pawns.BLACK_PAWN)

            for row, column in self.white_pawns:
                self.draw_pawn(screen, square_size, row, column, Pawns.WHITE_PAWN)

            pygame.display.flip()
