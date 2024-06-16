import pygame
import logging
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)


class BoardGUI:
    """
    Class for the graphical representation of the board
    """

    BACKGROUND_COLORS = [(230, 210, 170), (170, 120, 90)]

    def __init__(self, board_logic, screen):
        """
        Initialize the board, set the size and positions of pawns
        """
        # Initialize logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        self.logger = logger

        # Initialize rest of the attributes
        self.board_logic = board_logic
        self.screen = screen
        self.screen_size = screen.get_width()
        self.square_size = self.screen_size // self.board_logic.size

        self.logger.info(f"Initializing board with attributes:")
        self.logger.info(f"Board size: {self.board_logic.size}")
        self.logger.info(f"Number of pawns rows: {self.board_logic.pawn_rows}")
        self.logger.info(f"Screen size: {self.screen_size}")
        self.logger.info(f"Square size: {self.square_size}")

        self.draw_board()

    def draw_board(self):
        """
        Main drawing function
        """
        highligh_squares = []
        previous_click = None
        current_click = None
        self.board_logic.running = True
        while self.board_logic.running:
            # Draw the board
            for row in range(self.board_logic.size):
                color_index = row % 2
                for column in range(self.board_logic.size):
                    square = (
                        column * self.square_size,
                        row * self.square_size,
                        self.square_size,
                        self.square_size,
                    )
                    self.screen.fill(self.BACKGROUND_COLORS[color_index], square)
                    color_index = (color_index + 1) % 2

            # Draw the pawns
            for row, column in self.board_logic.black_pawns:
                self.draw_pawn(row, column, self.board_logic.Pawns.BLACK_PAWN)

            for row, column in self.board_logic.white_pawns:
                self.draw_pawn(row, column, self.board_logic.Pawns.WHITE_PAWN)

            for row, column in self.board_logic.black_queens:
                self.draw_pawn(row, column, self.board_logic.Pawns.BLACK_QUEEN)

            for row, column in self.board_logic.white_queens:
                self.draw_pawn(row, column, self.board_logic.Pawns.WHITE_QUEEN)


            if self.board_logic.turn == "black":
                self.logger.debug("AI's turn")
                #self.board_logic.random_move()
                pygame.display.flip()
                self.board_logic.ai_move(depth=2)
                continue

            # Handle events
            for event in [pygame.event.wait()] + pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    current_click = self.get_mouse_click_position()
                    if previous_click:
                        if self.board_logic.make_move(
                            previous_click[0],
                            previous_click[1],
                            current_click[0],
                            current_click[1],
                            possible_moves,
                        ):
                            previous_click = [None, None]
                            current_click = [None, None]

                    highligh_squares = []
                    possible_moves = self.board_logic.get_possible_moves(*current_click)
                    for move in possible_moves:
                        highligh_squares.append(move[-1])

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.board_logic.running = False

                elif event.type == QUIT:
                    self.board_logic.running = False

            # Highlight possible moves
            self.highlight_possible_moves(highligh_squares)
            previous_click = current_click
            pygame.display.flip()

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
        if pawn.value["type"] == "queen":
            # draw pawn with 'Q' letter in the middle
            font = pygame.font.Font(None, 60)
            pawn_color = pawn.value["color"]
            # invert the color of the pawn to make the text readable
            text = font.render(
                "Q",
                True,
                (255 - pawn_color[0], 255 - pawn_color[1], 255 - pawn_color[2]),
            )
            text_rect = text.get_rect(center=(pawn_x, pawn_y))
            self.screen.blit(text, text_rect)

    def get_mouse_click_position(self):
        """
        Get the position of the mouse click
        """
        x, y = pygame.mouse.get_pos()
        row = y // self.square_size
        column = x // self.square_size
        self.logger.debug(f"Clicked position: ({row}, {column})")
        return row, column
