import csv
from collections import deque
from animation_utils import animate_solution_with_original


class Vehicle:
    def __init__(self, vid, x, y, orientation, length):
        self.vid = vid
        self.row = int(y)
        self.col = int(x)
        self.orientation = orientation
        self.length = int(length)


class RushHourPuzzle:
    def __init__(self):
        self.board_height = 0
        self.board_width = 0
        self.vehicles = []
        self.walls = []
        self.board = []

    def setVehicles(self, filename):
        with open(filename, newline="") as f:
            reader = csv.reader(f)
            lines = list(reader)

        self.board_height, self.board_width = map(int, lines[0])
        self.vehicles = []
        self.walls = []

        for line in lines[1:]:
            if line[0] == "#":
                x, y = int(line[1]), int(line[2])
                self.walls.append((y, x))
            else:
                vid, x, y, orientation, length = line
                self.vehicles.append(Vehicle(vid, x, y, orientation, length))

    def setBoard(self):
        self.board = [["." for _ in range(self.board_width)] for _ in range(self.board_height)]

        for v in self.vehicles:
            if v.orientation == "H":
                for i in range(v.length):
                    self.board[v.row][v.col + i] = v.vid
            else:
                for i in range(v.length):
                    self.board[v.row + i][v.col] = v.vid

        for (r, c) in self.walls:
            self.board[r][c] = "#"

    def display(self):
        for row in self.board:
            print(" ".join(row))
        print()

    def isGoal(self):
        for v in self.vehicles:
            if v.vid == "X":
                if v.orientation == "H" and v.col + v.length - 1 == self.board_width - 1:
                    return True
        return False

    def successorFunction(self):
        successors = []
        for v in self.vehicles:
            if v.orientation == "H":
                if v.col > 0 and self.board[v.row][v.col - 1] == ".":
                    new_state = self._copy_state()
                    new_state._moveVehicle(v.vid, -1)
                    successors.append(((v.vid, "L"), new_state))

                if v.col + v.length < self.board_width and self.board[v.row][v.col + v.length] == ".":
                    new_state = self._copy_state()
                    new_state._moveVehicle(v.vid, 1)
                    successors.append(((v.vid, "R"), new_state))

            else:
                if v.row > 0 and self.board[v.row - 1][v.col] == ".":
                    new_state = self._copy_state()
                    new_state._moveVehicle(v.vid, -1)
                    successors.append(((v.vid, "U"), new_state))

                if v.row + v.length < self.board_height and self.board[v.row + v.length][v.col] == ".":
                    new_state = self._copy_state()
                    new_state._moveVehicle(v.vid, 1)
                    successors.append(((v.vid, "D"), new_state))
        return successors

    def _copy_state(self):
        new_puzzle = RushHourPuzzle()
        new_puzzle.board_height = self.board_height
        new_puzzle.board_width = self.board_width
        new_puzzle.vehicles = [Vehicle(v.vid, v.col, v.row, v.orientation, v.length) for v in self.vehicles]
        new_puzzle.walls = list(self.walls)
        new_puzzle.setBoard()
        return new_puzzle

    def _moveVehicle(self, vid, step):
        for v in self.vehicles:
            if v.vid == vid:
                if v.orientation == "H":
                    v.col += step
                else:
                    v.row += step
                break
        self.setBoard()


# =============================
# Node class (same as before)
# =============================
class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action

    def getPath(self):
        node, path = self, []
        while node:
            path.append(node.state)
            node = node.parent
        return list(reversed(path))

    def getSolution(self):
        node, actions = self, []
        while node and node.action:
            actions.append(node.action)
            node = node.parent
        return list(reversed(actions))


# =============================
# BFS (exactly your teacher’s version)
# =============================
def BFS(initial_puzzle):
    def successorsFn(state):
        return state.successorFunction()

    def isGoal(state):
        return state.isGoal()

    # initialize
    Open = deque()
    Closed = []

    init_node = Node(initial_puzzle, None, None)
    if isGoal(init_node.state):
        return init_node

    Open.append(init_node)

    while Open:
        current = Open.popleft()
        Closed.append(current.state)

        for action, successor in successorsFn(current.state):
            child = Node(successor, current, action)
            if isGoal(child.state):
                return child

            # Avoid revisiting states
            if all(not same_state(child.state, n.state) for n in Open) and all(
                not same_state(child.state, s) for s in Closed
            ):
                Open.append(child)

    return None


def same_state(p1, p2):
    """Compare two RushHourPuzzle states by vehicle positions"""
    return all(
        (v1.vid == v2.vid and v1.row == v2.row and v1.col == v2.col)
        for v1, v2 in zip(sorted(p1.vehicles, key=lambda x: x.vid),
                          sorted(p2.vehicles, key=lambda x: x.vid))
    )


# =============================
# Test BFS
# =============================
if __name__ == "__main__":
    puzzle = RushHourPuzzle()  

    # Choose the puzzle CSV file
    puzzle.setVehicles("1.csv")   # first CSV
    # puzzle.setVehicles("2-a.csv")  # second CSV
    # puzzle.setVehicles("2-b.csv") # third CSV with wall
    # puzzle.setVehicles("2-c.csv") # fourth CSV with wall
    # puzzle.setVehicles("2-d.csv") # fifth CSV with wall
    # puzzle.setVehicles("2-e.csv") # sixth CSV with wall
    # puzzle.setVehicles("e-f.csv") # seventh CSV with wall

    puzzle.setBoard()
    puzzle.display()

    print("Is goal?", puzzle.isGoal())

    solution_node = BFS(puzzle)

    if solution_node:
        animate_solution_with_original(puzzle, solution_node)
        print("Solution found!")
        print("Actions:", solution_node.getSolution())
    else:
        print("No solution found.")
