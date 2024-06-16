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

        BLACK_PAWN = {"index": 1, "color": (0, 0, 0), "player": "black", "type": "pawn"}
        WHITE_PAWN = {
            "index": 2,
            "color": (255, 255, 255),
            "player": "white",
            "type": "pawn",
        }
        BLACK_QUEEN = {
            "index": 3,
            "color": (0, 0, 0),
            "player": "black",
            "type": "queen",
        }
        WHITE_QUEEN = {
            "index": 4,
            "color": (255, 255, 255),
            "player": "white",
            "type": "queen",
        }

    def __init__(self, screen_size, size=8, pawns_rows=2):
        self.running = False
        self.size = size
        self.pawn_rows = pawns_rows
        self.turn = self.Pawns.WHITE_PAWN.value["player"]

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
        self.white_queens = []
        self.black_queens = []

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
        elif (row, column) in self.black_queens:
            position_pawn = self.Pawns.BLACK_QUEEN
        elif (row, column) in self.white_queens:
            position_pawn = self.Pawns.WHITE_QUEEN
        self.logger.debug(f"Position ({row}, {column}) pawn: {position_pawn}")
        return position_pawn

    def get_queen_moves(self, row, column, pawn, previous_position=None):
        """
        Get possible moves for the queen on the given position
        """
        possible_normal_moves = []
        possible_capture_moves = []

        for direction in [
            (1, -1),
            (1, 1),
            (-1, -1),
            (-1, 1),
        ]:
            next_position = (row + direction[0], column + direction[1])
            while self.field_exists(*next_position) and not self.check_position(
                *next_position
            ):
                move = [(row, column), next_position]
                possible_normal_moves.append(move)
                self.logger.debug(f"Possible normal move path: {move}")
                next_position = (
                    next_position[0] + direction[0],
                    next_position[1] + direction[1],
                )

            if self.field_exists(*next_position):
                in_capture_position = self.check_position(*next_position)
                capture_position = next_position
                if (
                    in_capture_position
                    and in_capture_position.value["player"] != pawn.value["player"]
                ):
                    if capture_position[1] < column:
                        next_column = capture_position[1] - 1
                    elif capture_position[1] > column:
                        next_column = capture_position[1] + 1
                    next_position = (capture_position[0] + direction[0], next_column)
                    if not self.field_exists(*next_position):
                        continue
                    if not self.check_position(*next_position):
                        move = [(row, column), capture_position, next_position]
                        possible_capture_moves.append(move)
                        self.logger.debug(f"Possible capture move path: {move}")
                        possible_capture_moves.extend(
                            self.get_queen_capture_moves(move, pawn)
                        )

        return possible_normal_moves, possible_capture_moves

    def get_queen_capture_moves(self, path, pawn):
        """
        Get possible capture moves for the queen on the given position from the given path
        """

        possible_capture_moves = []

        directions = [
            (1, -1),
            (1, 1),
            (-1, -1),
            (-1, 1),
        ]
        if path:
            current_position = path[-1]

        for direction in directions:
            capture_position = (
                current_position[0] + direction[0],
                current_position[1] + direction[1],
            )
            if capture_position in path:
                self.logger.debug(
                    f"Capture position {capture_position} already in path, skipping"
                )
                continue
            next_position = (
                capture_position[0] + direction[0],
                capture_position[1] + direction[1],
            )
            if not self.field_exists(*capture_position) or self.check_position(
                *next_position
            ):
                continue
            on_capture_position = self.check_position(*capture_position)
            on_next_position = self.check_position(*next_position)
            if not on_capture_position or on_next_position:
                continue
            if on_capture_position.value["player"] != pawn.value["player"]:
                move = path.copy()
                move.append(capture_position)
                move.append(next_position)
                possible_capture_moves.append(move)
                self.logger.debug(f"Possible capture move path: {move}")
                possible_capture_moves.extend(self.get_queen_capture_moves(move, pawn))

        return possible_capture_moves

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
            if (
                in_neighbour_position
                and in_neighbour_position.value["player"] != pawn.value["player"]
            ):
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

        if pawn.value["type"] == "queen":
            normal_queen_moves, capture_queen_moves = self.get_queen_moves(
                row, column, pawn
            )
            possible_moves.extend(normal_queen_moves)
            possible_moves.extend(capture_queen_moves)
        else:
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
                pawn_on_path = self.check_position(*path_position)
                if pawn_on_path:
                    player = pawn_on_path.value["player"]
                    pawn_type = pawn_on_path.value["type"]
                    if player == "black":
                        if pawn_type == "pawn":
                            self.black_pawns.remove(path_position)
                            self.logger.info(
                                f"Black pawn removed from: {path_position}!"
                            )
                        elif pawn_type == "queen":
                            self.black_queens.remove(path_position)
                            self.logger.info(
                                f"Black queen removed from: {path_position}!"
                            )
                    elif player == "white":
                        if pawn_type == "pawn":
                            self.white_pawns.remove(path_position)
                            self.logger.info(
                                f"White pawn removed from: {path_position}!"
                            )
                        elif pawn_type == "queen":
                            self.white_queens.remove(path_position)
                            self.logger.info(
                                f"White queen removed from: {path_position}!"
                            )

            # Remove the pawn from the start position and add it to the destination position
            if pawn == self.Pawns.BLACK_PAWN:
                self.black_pawns.remove((row, column))
                self.black_pawns.append((next_row, next_column))
            elif pawn == self.Pawns.WHITE_PAWN:
                self.white_pawns.remove((row, column))
                self.white_pawns.append((next_row, next_column))
            elif pawn == self.Pawns.BLACK_QUEEN:
                self.black_queens.remove((row, column))
                self.black_queens.append((next_row, next_column))
            elif pawn == self.Pawns.WHITE_QUEEN:
                self.white_queens.remove((row, column))
                self.white_queens.append((next_row, next_column))

            self.logger.info(f"Move made: {move[0]} -> {move[-1]}")

            if move[-1][0] == 0 or move[-1][0] == self.size - 1:
                self.make_queen(move[-1])

            # Change the turn
            self.change_turn()
            break

        return move_made

    def make_queen(self, position):
        """
        Make a queen from the pawn on the given position
        """
        pawn = self.check_position(*position)
        if not pawn:
            return
        if pawn == self.Pawns.BLACK_PAWN:
            self.black_pawns.remove(position)
            self.black_queens.append(position)
            self.logger.info(f"Black pawn promoted to queen: {position}")
        elif pawn == self.Pawns.WHITE_PAWN:
            self.white_pawns.remove(position)
            self.white_queens.append(position)
            self.logger.info(f"White pawn promoted to queen: {position}")

    def change_turn(self):
        """
        Change the turn
        """
        if self.all_pawns_lost():
            self.finish_game(winner=self.turn)
            return

        self.turn = (
            self.Pawns.BLACK_PAWN.value["player"]
            if self.turn == self.Pawns.WHITE_PAWN.value["player"]
            else self.Pawns.WHITE_PAWN.value["player"]
        )
        self.logger.info(f"Turn changed to: {self.turn}")

        if not self.has_possible_move():
            self.logger.info(f"No possible moves for {self.turn}!")
            self.turn = (
                self.Pawns.BLACK_PAWN.value["player"]
                if self.turn == self.Pawns.WHITE_PAWN.value["player"]
                else self.Pawns.WHITE_PAWN.value["player"]
            )
            self.logger.info(f"Turn changed to: {self.turn}")
            if not self.has_possible_move():
                self.logger.info(f"No possible moves for {self.turn} either!")
                self.finish_game(winner=None)

    def is_pawn_turn(self, pawn):
        """
        Check if it is the turn of the given pawn
        """
        if self.turn != pawn.value["player"]:
            self.logger.info(f"It is not {pawn} turn!")
            return False
        return True

    def get_all_pawns(self, player):
        """
        Get all pawns of the given player
        """
        if player == "white":
            return self.white_pawns + self.white_queens
        else:
            return self.black_pawns + self.black_queens

    def has_possible_move(self):
        """
        Check if the current player has any possible move
        """
        if self.turn == "white":
            pawns = self.get_all_pawns("white")
        else:
            pawns = self.get_all_pawns("black")

        for row, column in pawns:
            if self.get_possible_moves(row, column):
                return True
        return False

    def all_pawns_lost(self):
        """
        Check if all pawns of one of the players are lost
        """
        if not self.get_all_pawns("white") or not self.get_all_pawns("black"):
            return True
        return False

    def finish_game(self, winner):
        """
        Finish the game and show the winner
        """
        white_pawns_count = len(self.get_all_pawns("white"))
        black_pawns_count = len(self.get_all_pawns("black"))
        self.logger.info("Game over!")
        if not winner and white_pawns_count == black_pawns_count:
            self.logger.info(
                f"Both players have the same number of pawns: {white_pawns_count} = {black_pawns_count}"
            )
            self.logger.info("It's a draw!")

        if black_pawns_count > white_pawns_count:
            self.logger.info(
                f"Black player has more pawns: {black_pawns_count} > {white_pawns_count}"
            )
            winner = self.Pawns.BLACK_PAWN.value["player"]
        elif white_pawns_count > black_pawns_count:
            self.logger.info(
                f"White player has more pawns: {white_pawns_count} > {black_pawns_count}"
            )
            winner = self.Pawns.WHITE_PAWN.value["player"]

        self.logger.info(f"The winner is: {winner}")
        self.running = False
