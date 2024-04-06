import pygame
from enum import Enum
import logging

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
    """
    Enum class for pawns
    Each pawn has an index and a color
    """

    BLACK_PAWN = {"index": 1, "color": (0, 0, 0)}
    WHITE_PAWN = {"index": 2, "color": (255, 255, 255)}


class Board:
    """
    Class representing the board
    Board has adjustable size
    It contains list of positions for each type of pawns
    """

    white_pawns = []
    black_pawns = []
    size = 0

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    def __init__(self, size, pawns_rows=2):
        """
        Initialize the board, set the size and positions of pawns
        """
        self.size = size
        self.pawns_rows = pawns_rows
        self.logger.info(
            f"Initializing board with size: {size} and number of pawn rows: {pawns_rows}"
        )

        for column in range(size):
            for row in range(pawns_rows):
                if (row + column) % 2 == 1:
                    self.black_pawns.append((row, column))

            for row in range(size - pawns_rows, size):
                if (row + column) % 2 == 1:
                    self.white_pawns.append((row, column))

        self.logger.debug(f"Black pawns positions: {self.black_pawns}")
        self.logger.debug(f"White pawns positions: {self.white_pawns}")

    def field_exists(self, row, column):
        """
        Check if field exists on the board
        """
        exists = row >= 0 and row < self.size and column >= 0 and column < self.size
        self.logger.debug(f"Position ({row}, {column}) exists: {exists}")
        return exists

    def check_position(self, row, column):
        """
        Check if there is a pawn on the given position and return its type
        """
        position_pawn = None
        if (row, column) in self.black_pawns:
            position_pawn = Pawns.BLACK_PAWN
        elif (row, column) in self.white_pawns:
            position_pawn = Pawns.WHITE_PAWN
        self.logger.debug(f"Position ({row}, {column}) pawn: {position_pawn}")
        return position_pawn

    def get_capture_moves(self, row, column, pawn):
        """
        Get possible capture moves for the pawn on the given position
        """
        possible_capture_moves = []

        if pawn == Pawns.BLACK_PAWN:
            direction = 1
        elif pawn == Pawns.WHITE_PAWN:
            direction = -1

        for position in [
            (row + direction * 1, column - 1),
            (row + direction * 1, column + 1),
        ]:
            if not self.field_exists(*position):
                continue
            in_position = self.check_position(*position)
            if in_position and in_position != pawn:
                if position[1] < column:
                    next_column = position[1] - 1
                elif position[1] > column:
                    next_column = position[1] + 1
                next_position = (position[0] + direction * 1, next_column)
                if not self.field_exists(*next_position):
                    continue
                if not self.check_position(*next_position):
                    possible_capture_moves.append(next_position)
                    self.logger.debug(
                        f"Possible capture move from position ({row}, {column}): ({next_position[0]}, {next_position[1]}))"
                    )
                    possible_capture_moves.extend(
                        self.get_capture_moves(*next_position, pawn)
                    )
        return possible_capture_moves

    def get_normal_moves(self, row, column, pawn):
        """
        Get possible normal moves for the pawn on the given position
        """
        possible_normal_moves = []

        if pawn == Pawns.BLACK_PAWN:
            direction = 1
        elif pawn == Pawns.WHITE_PAWN:
            direction = -1

        for position in [
            (row + direction * 1, column - 1),
            (row + direction * 1, column + 1),
        ]:
            if not self.field_exists(*position):
                continue
            if not self.check_position(*position):
                possible_normal_moves.append(position)
                self.logger.debug(
                    f"Possible normal move from position ({row}, {column}): ({position[0]}, {position[1]}))"
                )
        return possible_normal_moves

    def get_possible_moves(self, row, column):
        """
        Get possible capture and normal moves for the pawn on the given position
        """
        possible_moves = []

        pawn = self.check_position(row, column)
        if not pawn:
            return possible_moves

        possible_moves.extend(self.get_normal_moves(row, column, pawn))
        possible_moves.extend(self.get_capture_moves(row, column, pawn))

        return possible_moves

    def highlight_possible_moves(self, screen, square_size, possible_moves):
        """
        Highlight possible moves on the board
        """
        for move in possible_moves:
            row, column = move
            square = (
                column * square_size,
                row * square_size,
                square_size,
                square_size,
            )
            pygame.draw.rect(screen, (0, 255, 0), square)

    def draw_pawn(self, screen, square_size, row, column, pawn):
        """
        Draw a pawn on the board
        """
        pawn_radius = square_size // 3
        pawn_x = column * square_size + square_size // 2
        pawn_y = row * square_size + square_size // 2
        pygame.draw.circle(screen, pawn.value["color"], (pawn_x, pawn_y), pawn_radius)

    def draw_board(self, screen):
        """
        Main drawing function
        """
        BACKGROUND_COLORS = [(230, 210, 170), (170, 120, 90)]
        screen_size = screen.get_width()
        square_size = screen_size // self.size

        running = True
        while running:
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

            # Handle events
            for event in [pygame.event.wait()] + pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    column = x // square_size
                    row = y // square_size
                    self.logger.debug(f"Clicked position: ({row}, {column})")
                    self.highlight_possible_moves(
                        screen, square_size, self.get_possible_moves(row, column)
                    )
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False

                elif event.type == QUIT:
                    running = False

            pygame.display.flip()
