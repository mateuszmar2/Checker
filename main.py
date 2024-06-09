from BoardLogic import BoardLogic


def main():
    """
    Main function of the game
    """
    screen_size = 800
    board_size = 8
    pawns_rows = 2
    BoardLogic(screen_size, board_size, pawns_rows)


if __name__ == "__main__":
    main()
