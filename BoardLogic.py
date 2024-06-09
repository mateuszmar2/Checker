import pygame
from enum import Enum
import logging
from BoardGUI import *


class BoardLogic:
    """
    Class for the logic of the board
    """

    class Pawns(Enum):
        """
        Enum class for pawns
        Each pawn has an index and a color
        """

        BLACK_PAWN = {"index": 1, "color": (0, 0, 0)}
        WHITE_PAWN = {"index": 2, "color": (255, 255, 255)}

    def __init__(self, screen_size, size=8, pawns_rows=2):
        self.running = False
        self.size = size
        self.pawn_rows = pawns_rows
        self.turn = self.Pawns.WHITE_PAWN

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

        # Initialize pawn positions
        self.white_pawns = []
        self.black_pawns = []

        for column in range(self.size):
            for row in range(pawns_rows):
                if (row + column) % 2 == 1:
                    self.black_pawns.append((row, column))

            for row in range(size - pawns_rows, self.size):
                if (row + column) % 2 == 1:
                    self.white_pawns.append((row, column))

        self.logger.debug(f"Black pawns positions: {self.black_pawns}")
        self.logger.debug(f"White pawns positions: {self.white_pawns}")

        # Initialize GUI
        pygame.init()
        pygame.display.set_caption("Warcaby")
        screen = pygame.display.set_mode((screen_size, screen_size))
        self.GUI = BoardGUI(self, screen)

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
            position_pawn = self.Pawns.BLACK_PAWN
        elif (row, column) in self.white_pawns:
            position_pawn = self.Pawns.WHITE_PAWN
        self.logger.debug(f"Position ({row}, {column}) pawn: {position_pawn}")
        return position_pawn

    def get_capture_moves(self, row, column, pawn, path):
        """
        Get possible capture moves for the pawn on the given position
        """
        possible_capture_moves = []

        if pawn == self.Pawns.BLACK_PAWN:
            direction = 1
        elif pawn == self.Pawns.WHITE_PAWN:
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
                    move = path.copy()
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

        if pawn == self.Pawns.BLACK_PAWN:
            direction = 1
        elif pawn == self.Pawns.WHITE_PAWN:
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
        elif not self.is_pawn_turn(pawn):
            return possible_moves

        possible_moves.extend(self.get_capture_moves(row, column, pawn, []))
        possible_moves.extend(self.get_normal_moves(row, column, pawn))

        return possible_moves

    def make_move(self, row, column, next_row, next_column, possible_moves):
        """
        Make a move on the board
        """
        move_made = False
        pawn = self.check_position(row, column)
        if not pawn:
            return move_made
        elif not self.is_pawn_turn(pawn):
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
            if pawn == self.Pawns.BLACK_PAWN:
                self.black_pawns.remove((row, column))
                self.black_pawns.append((next_row, next_column))
            elif pawn == self.Pawns.WHITE_PAWN:
                self.white_pawns.remove((row, column))
                self.white_pawns.append((next_row, next_column))

            self.logger.info(f"Move made: {move[0]} -> {move[-1]}")

            # Change the turn
            self.change_turn()
            break

        return move_made

    def change_turn(self):
        """
        Change the turn
        """
        if self.all_pawns_lost():
            self.finish_game(winner=self.turn)
            return

        self.turn = (
            self.Pawns.BLACK_PAWN
            if self.turn == self.Pawns.WHITE_PAWN
            else self.Pawns.WHITE_PAWN
        )
        self.logger.info(f"Turn changed to: {self.turn}")

        if not self.has_possible_move():
            self.logger.info(f"No possible moves for {self.turn}!")
            self.turn = (
                self.Pawns.BLACK_PAWN
                if self.turn == self.Pawns.WHITE_PAWN
                else self.Pawns.WHITE_PAWN
            )
            self.logger.info(f"Turn changed to: {self.turn}")
            if not self.has_possible_move():
                self.logger.info(f"No possible moves for {self.turn} either!")
                self.finish_game(winner=None)

    def is_pawn_turn(self, pawn):
        """
        Check if it is the turn of the given pawn
        """
        if self.turn != pawn:
            self.logger.info(f"It is not {pawn} turn!")
            return False
        return True

    def has_possible_move(self):
        """
        Check if the current player has any possible move
        """
        for row, column in (
            self.black_pawns if self.turn == self.Pawns.BLACK_PAWN else self.white_pawns
        ):
            if self.get_possible_moves(row, column):
                return True
        return False

    def all_pawns_lost(self):
        """
        Check if all pawns of one of the players are lost
        """
        if not self.white_pawns or not self.black_pawns:
            return True
        return False

    def finish_game(self, winner):
        """
        Finish the game and show the winner
        """
        self.logger.info("Game over!")
        if not winner and len(self.black_pawns) == len(self.white_pawns):
                self.logger.info(f"Both players have the same number of pawns: {len(self.black_pawns)}")
                self.logger.info("It's a draw!")

        if len(self.black_pawns) > len(self.white_pawns):
            self.logger.info(f"Black player has more pawns: {len(self.black_pawns)} > {len(self.white_pawns)}")
            winner = self.Pawns.BLACK_PAWN
        elif len(self.black_pawns) < len(self.white_pawns):
            self.logger.info(f"White player has more pawns: {len(self.white_pawns)} > {len(self.black_pawns)}")
            winner = self.Pawns.WHITE_PAWN

        self.logger.info(f"The winner is: {winner}")
        self.running = False
