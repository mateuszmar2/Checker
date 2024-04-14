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

    BACKGROUND_COLORS = [(230, 210, 170), (170, 120, 90)]
    size = 0
    pawns_rows = 0

    screen = None
    screen_size = 0
    square_size = 0

    white_pawns = []
    black_pawns = []

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    def __init__(self, screen, size=8, pawns_rows=2):
        """
        Initialize the board, set the size and positions of pawns
        """
        self.size = size
        self.pawns_rows = pawns_rows

        self.screen = screen
        self.screen_size = screen.get_width()
        self.square_size = self.screen_size // self.size

        self.logger.info(f"Initializing board with attributes:")
        self.logger.info(f"Board size: {self.size}")
        self.logger.info(f"Number of pawns rows: {self.pawns_rows}")
        self.logger.info(f"Screen size: {self.screen_size}")
        self.logger.info(f"Square size: {self.square_size}")

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

    def get_capture_moves(self, row, column, pawn, path):
        """
        Get possible capture moves for the pawn on the given position
        """
        possible_capture_moves = []

        if pawn == Pawns.BLACK_PAWN:
            direction = 1
        elif pawn == Pawns.WHITE_PAWN:
            direction = -1

        for neighbour_position in [
            (row + direction * 1, column - 1),
            (row + direction * 1, column + 1),
        ]:
            if not self.field_exists(*neighbour_position):
                continue
            in_neighbour_position = self.check_position(*neighbour_position)
            if in_neighbour_position and in_neighbour_position != pawn:
                if neighbour_position[1] < column:
                    next_column = neighbour_position[1] - 1
                elif neighbour_position[1] > column:
                    next_column = neighbour_position[1] + 1
                next_position = (neighbour_position[0] + direction * 1, next_column)
                if not self.field_exists(*next_position):
                    continue
                if not self.check_position(*next_position):
                    move = path
                    move.append((row, column))
                    move.append(neighbour_position)
                    move.append(next_position)
                    possible_capture_moves.append(move)
                    self.logger.debug(f"Possible capture move path: {move}")
                    # Pass new list to avoid modifying the original path
                    possible_capture_moves.extend(
                        self.get_capture_moves(*next_position, pawn, path=move[:])
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

        for next_position in [
            (row + direction * 1, column - 1),
            (row + direction * 1, column + 1),
        ]:
            if not self.field_exists(*next_position):
                continue
            if not self.check_position(*next_position):
                move = [(row, column), next_position]
                possible_normal_moves.append(move)
                self.logger.debug(f"Possible normal move path: {move}")
        return possible_normal_moves

    def get_possible_moves(self, row, column):
        """
        Get possible capture and normal moves for the pawn on the given position
        """
        possible_moves = []

        pawn = self.check_position(row, column)
        if not pawn:
            return possible_moves

        possible_moves.extend(self.get_capture_moves(row, column, pawn, []))
        possible_moves.extend(self.get_normal_moves(row, column, pawn))

        return possible_moves

    def highlight_possible_moves(self, possible_moves):
        """
        Highlight possible moves on the board
        """
        for move in possible_moves:
            row, column = move
            square = (
                column * self.square_size,
                row * self.square_size,
                self.square_size,
                self.square_size,
            )
            pygame.draw.rect(self.screen, (0, 255, 0), square)

    def draw_pawn(self, row, column, pawn):
        """
        Draw a pawn on the board
        """
        pawn_radius = self.square_size // 3
        pawn_x = column * self.square_size + self.square_size // 2
        pawn_y = row * self.square_size + self.square_size // 2
        pygame.draw.circle(
            self.screen, pawn.value["color"], (pawn_x, pawn_y), pawn_radius
        )

    def get_mouse_click_position(self):
        """
        Get the position of the mouse click
        """
        x, y = pygame.mouse.get_pos()
        row = y // self.square_size
        column = x // self.square_size
        self.logger.debug(f"Clicked position: ({row}, {column})")
        return row, column

    def make_move(self, row, column, next_row, next_column, possible_moves):
        """
        Make a move on the board
        """
        move_made = False
        pawn = self.check_position(row, column)
        if not pawn:
            return move_made

        for move in possible_moves:
            if (next_row, next_column) != move[-1]:
                continue

            move_made = True
            # Clear all pawns on the path
            for path_position in move[1:]:
                if path_position in self.black_pawns:
                    self.black_pawns.remove(path_position)
                    self.logger.info(f"Black pawn removed from: {path_position}!")
                elif path_position in self.white_pawns:
                    self.white_pawns.remove(path_position)
                    self.logger.info(f"White pawn removed from: {path_position}!")

            # Remove the pawn from the start position and add it to the destination position
            if pawn == Pawns.BLACK_PAWN:
                self.black_pawns.remove((row, column))
                self.black_pawns.append((next_row, next_column))
            elif pawn == Pawns.WHITE_PAWN:
                self.white_pawns.remove((row, column))
                self.white_pawns.append((next_row, next_column))

            self.logger.info(f"Move made: {move[0]} -> {move[-1]}")

        return move_made

    def draw_board(self):
        """
        Main drawing function
        """
        highligh_squares = []
        previous_click = None
        current_click = None
        running = True
        while running:
            # Draw the board
            for row in range(self.size):
                color_index = row % 2
                for column in range(self.size):
                    square = (
                        column * self.square_size,
                        row * self.square_size,
                        self.square_size,
                        self.square_size,
                    )
                    self.screen.fill(self.BACKGROUND_COLORS[color_index], square)
                    color_index = (color_index + 1) % 2

            # Draw the pawns
            for row, column in self.black_pawns:
                self.draw_pawn(row, column, Pawns.BLACK_PAWN)

            for row, column in self.white_pawns:
                self.draw_pawn(row, column, Pawns.WHITE_PAWN)

            # Handle events
            for event in [pygame.event.wait()] + pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    current_click = self.get_mouse_click_position()
                    if previous_click:
                        if self.make_move(
                            previous_click[0],
                            previous_click[1],
                            current_click[0],
                            current_click[1],
                            possible_moves,
                        ):
                            previous_click = [None, None]
                            current_click = [None, None]

                    highligh_squares = []
                    possible_moves = self.get_possible_moves(*current_click)
                    for move in possible_moves:
                        highligh_squares.append(move[-1])

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False

                elif event.type == QUIT:
                    running = False

            # Highlight possible moves
            self.highlight_possible_moves(highligh_squares)
            previous_click = current_click
            pygame.display.flip()
