import pygame
from enum import Enum
import logging
from BoardGUI import *
import random
import hashlib


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
        self.transposition_table = {}

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

        self.logger.debug(f"Possible moves: {possible_moves}")
        return possible_moves

    def ai_get_possible_moves(self, row, column):
        """
        Same as get_possible_moves, but without checking turn
        """
        possible_moves = []

        pawn = self.check_position(row, column)
        if not pawn:
            return possible_moves

        possible_moves.extend(self.get_capture_moves(row, column, pawn, []))
        possible_moves.extend(self.get_normal_moves(row, column, pawn))

        self.logger.debug(f"[AI] Possible moves: {possible_moves}")
        return possible_moves

    def make_move(self, row, column, next_row, next_column, possible_moves):
        """
        Make a move on the board
        """
        move_made = False
        pawn = self.check_position(row, column)
        self.logger.debug(f"Making move: ({row}, {column}) to ({next_row}, {next_column})")
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
                    self.logger.debug(f"Black pawn removed from: {path_position}!")
                elif path_position in self.white_pawns:
                    self.white_pawns.remove(path_position)
                    self.logger.debug(f"White pawn removed from: {path_position}!")

            # Remove the pawn from the start position and add it to the destination position
            if pawn == self.Pawns.BLACK_PAWN:
                self.black_pawns.remove((row, column))
                self.black_pawns.append((next_row, next_column))
            elif pawn == self.Pawns.WHITE_PAWN:
                self.white_pawns.remove((row, column))
                self.white_pawns.append((next_row, next_column))

            self.logger.debug(f"Move made: {move[0]} -> {move[-1]}")

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
        self.logger.debug(f"Turn changed to: {self.turn}")

        if not self.has_possible_move():
            self.logger.debug(f"No possible moves for {self.turn}!")
            self.turn = (
                self.Pawns.BLACK_PAWN
                if self.turn == self.Pawns.WHITE_PAWN
                else self.Pawns.WHITE_PAWN
            )
            self.logger.debug(f"Turn changed to: {self.turn}")
            if not self.has_possible_move():
                self.logger.debug(f"No possible moves for {self.turn} either!")
                self.finish_game(winner=None)

    def is_pawn_turn(self, pawn):
        """
        Check if it is the turn of the given pawn
        """
        if self.turn != pawn:
            self.logger.debug(f"It is not {pawn} turn!")
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

    def ai_has_possible_move(self):
        """
        Check if the AI has any possible move
        """
        for row, column in self.black_pawns if self.turn == self.Pawns.BLACK_PAWN else self.white_pawns:
            if self.ai_get_possible_moves(row, column):
                return True
        return False

    def get_all_pawns(self, pawn_type):
        return self.black_pawns if pawn_type == self.Pawns.BLACK_PAWN else self.white_pawns

    def random_move(self):
        pawns = self.get_all_pawns(self.Pawns.BLACK_PAWN)
        random.shuffle(pawns)

        for row, column in pawns:
            moves = self.get_possible_moves(row, column)
            if moves:
                random_move = random.choice(moves)
                self.make_move(random_move[0][0], random_move[0][1], random_move[-1][0], random_move[-1][1], moves)
                return
        self.logger.debug("AI could not find a valid move.")

    def evaluate_board(self):
        """
        Evaluate the board and return a score based on an advanced heuristic.
        """
        black_score = 0
        white_score = 0

        # Piece count and position
        for row, column in self.black_pawns:
            black_score += 10  # Base score for pawn
            black_score += row  # Bonus for advancing pawns
        
        for row, column in self.white_pawns:
            white_score += 10  # Base score for pawn
            white_score += (self.size - 1 - row)  # Bonus for advancing pawns

        # Center control
        center_positions = self.get_center_positions()
        for row, column in self.black_pawns:
            if (row, column) in center_positions:
                black_score += 5

        for row, column in self.white_pawns:
            if (row, column) in center_positions:
                white_score += 5

        # Mobility
        black_moves = sum(len(self.ai_get_possible_moves(row, column)) for row, column in self.black_pawns)
        white_moves = sum(len(self.ai_get_possible_moves(row, column)) for row, column in self.white_pawns)
        black_score += black_moves
        white_score += white_moves

        # King count (if applicable, adjust this if you have implemented king logic)
        # black_score += len(self.black_kings) * 20
        # white_score += len(self.white_kings) * 20

        self.logger.debug(f"AI Board evaluation: black_score={black_score}, white_score={white_score}")

        return black_score - white_score

    def get_board_hash(self):
        board_state = (tuple(sorted(self.black_pawns)), tuple(sorted(self.white_pawns)), self.turn)
        return hashlib.sha1(str(board_state).encode()).hexdigest()

    def minimax(self, depth, alpha, beta, maximizing_player):
        """
        Minimax algorithm with alpha-beta pruning.
        """
        self.logger.debug(f"[AI] Enter minimax depth {depth} alpha {alpha} beta {beta}")

        board_hash = self.get_board_hash()
        if board_hash in self.transposition_table:
            return self.transposition_table[board_hash]

        self.logger.debug(f"[AI] No entry in hashmap, calculating moves")
        if depth == 0 or not self.ai_has_possible_move():
            score = self.evaluate_board()
            self.logger.debug(f"[AI] Minimax evaluation at depth 0: {score}")
            #self.transposition_table[board_hash] = (score, None)
            return score, None

        if maximizing_player:
            self.logger.debug(f"[AI] maximizing")
            max_eval = float('-inf')
            best_move = None
            for row, column in sorted(self.black_pawns):
                self.logger.debug(f"[AI][max] black pawn {row, column}")
                for move in sorted(self.ai_get_possible_moves(row, column), key=lambda m: -self.evaluate_move(m)):
                    self.logger.debug(f"[AI][max] considering move {move}")
                    captures = self.apply_move(move, self.Pawns.BLACK_PAWN)
                    eval, _ = self.minimax(depth - 1, alpha, beta, False)
                    self.logger.debug(f"[AI][max] move {move} evaluation: {eval}")
                    self.revert_move(move, self.Pawns.BLACK_PAWN, captures)
                    if eval > max_eval:
                        max_eval = eval
                        best_move = move
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            self.transposition_table[board_hash] = (max_eval, best_move)
            self.logger.debug(f"[AI][max] best move: {best_move} with evaluation: {max_eval}")
            return max_eval, best_move
        else:
            self.logger.debug(f"[AI] minimizing")
            min_eval = float('inf')
            best_move = None
            for row, column in sorted(self.white_pawns):
                self.logger.debug(f"[AI][min] white pawn {row, column}")
                for move in sorted(self.ai_get_possible_moves(row, column), key=lambda m: self.evaluate_move(m)):
                    self.logger.debug(f"[AI][min] considering move {move}")
                    captures = self.apply_move(move, self.Pawns.WHITE_PAWN)
                    eval, _ = self.minimax(depth - 1, alpha, beta, True)
                    self.logger.debug(f"[AI][min] move {move} evaluation: {eval}")
                    self.revert_move(move, self.Pawns.WHITE_PAWN, captures)
                    if eval < min_eval:
                        min_eval = eval
                        best_move = move
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            self.transposition_table[board_hash] = (min_eval, best_move)
            self.logger.debug(f"[AI][min] best move: {best_move} with evaluation: {min_eval}")
            return min_eval, best_move

    def apply_move(self, move, pawn):
        """
        Apply a move on the board without changing turns.
        """
        start, end = move[0], move[-1]
        captures = []
        self.logger.debug(f"AI Applying move: {move}")

        # Remove pawn from the start position and add to the end position
        if pawn == self.Pawns.BLACK_PAWN:
            self.black_pawns.remove(start)
            self.black_pawns.append(end)
        elif pawn == self.Pawns.WHITE_PAWN:
            self.white_pawns.remove(start)
            self.white_pawns.append(end)

        # Handle captures
        for capture in move[1:-1]:
            if capture in self.black_pawns:
                self.black_pawns.remove(capture)
                captures.append((capture, self.Pawns.BLACK_PAWN))
            elif capture in self.white_pawns:
                self.white_pawns.remove(capture)
                captures.append((capture, self.Pawns.WHITE_PAWN))

        return captures

    def revert_move(self, move, pawn, captures):
        """
        Revert a move on the board without changing turns.
        """
        start, end = move[0], move[-1]
        self.logger.debug(f"AI Reverting move: {move}")

        # Remove pawn from the end position and add to the start position
        if pawn == self.Pawns.BLACK_PAWN:
            self.black_pawns.remove(end)
            self.black_pawns.append(start)
        elif pawn == self.Pawns.WHITE_PAWN:
            self.white_pawns.remove(end)
            self.white_pawns.append(start)

        # Restore captures
        for capture, captured_pawn in captures:
            if captured_pawn == self.Pawns.BLACK_PAWN:
                self.black_pawns.append(capture)
            elif captured_pawn == self.Pawns.WHITE_PAWN:
                self.white_pawns.append(capture)


    def evaluate_move(self, move):
        """
        Evaluate a move based on its position and potential captures.
        """
        start, end = move[0], move[-1]
        score = 0

        # Calculate dynamic center positions
        center_positions = self.get_center_positions()

        # Assign higher score for moves ending in center positions
        if end in center_positions:
            score += 5  # Center positions are more valuable

        # Assign score for the length of the move (captures are more valuable)
        score += len(move) - 1  # Longer moves (captures) are more valuable

        return score


    def get_center_positions(self):
        """
        Determine the center positions of the board dynamically based on the board size.
        """
        center_positions = []
        center = self.size // 2

        # Define the size of the central region as a fraction of the board size
        central_region_size = max(2, self.size // 4)

        for row in range(center - central_region_size // 2, center + (central_region_size + 1) // 2):
            for col in range(center - central_region_size // 2, center + (central_region_size + 1) // 2):
                center_positions.append((row, col))

        return center_positions


    def ai_move(self, depth=3):
        """
        Perform the AI move using minimax.
        """
        self.logger.debug("AI is making a move.")
        _, best_move = self.minimax(depth, float('-inf'), float('inf'), True)
        if best_move:
            self.make_move(best_move[0][0], best_move[0][1], best_move[-1][0], best_move[-1][1], [best_move])
            self.logger.debug(f"AI made move: {best_move}")
        else:
            self.logger.debug("AI could not find a valid move.")
            self.change_turn()
