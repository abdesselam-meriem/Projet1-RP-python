import time
import os

# ANSI escape code for red text
RED = "\033[91m"
RESET = "\033[0m"

def animate_solution_with_original(puzzle, solution_node, delay=0.6):
    states = solution_node.getPath()
    actions = solution_node.getSolution()

    board_width = puzzle.board_width
    board_height = puzzle.board_height

    # Find the row where 'X' car is located in the puzzle (using current state)
    def get_exit_row(state):
        for v in state.vehicles:
            if v.vid == "X":
                return v.row
        return None

    # Print original puzzle once
    print("Original Puzzle:")
    print("    " + " ".join(str(c) for c in range(board_width)) + "   Exit -->")
    for r in range(board_height):
        print(f"{r:2} | " + " ".join(puzzle.board[r]) + " |")
    print("\nAnimating solution below:\n")

    for i, state in enumerate(states):
        os.system('cls' if os.name == 'nt' else 'clear')

        # Reprint original puzzle above
        print("Original Puzzle:")
        print("    " + " ".join(str(c) for c in range(board_width)) + "   Exit -->")
        for r in range(board_height):
            print(f"{r:2} | " + " ".join(puzzle.board[r]) + " |")

        print("\nAnimating solution below:\n")

        print("    " + " ".join(str(c) for c in range(board_width)) + "   Exit -->")

        exit_row = get_exit_row(state)

        for r in range(board_height):
            row_str = f"{r:2} | "
            for c in range(board_width):
                cell = state.board[r][c]
                if cell == "X":
                    cell = f"\033[91m{cell}\033[0m"  # red color
                row_str += cell + " "
            # Open exit border on the row where the red car 'X' is
            if r == exit_row:
                row_str = row_str.rstrip()  # remove trailing space, no '|'
            else:
                row_str += "|"
            print(row_str)

        print("\nMove:", i)
        if i > 0:
            print("Action:", actions[i - 1])
        time.sleep(delay)
