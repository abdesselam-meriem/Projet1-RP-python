import csv
from collections import deque
from animation_utils import animate_solution_with_original


class Vehicle:
    def __init__(self, vid, x, y, orientation, length):
        self.vid = vid
        self.row = int(y)              # row comes from 'y'
        self.col = int(x)              # col comes from 'x'
        self.orientation = orientation # 'H' or 'V'
        self.length = int(length)

class RushHourPuzzle:
    def __init__(self):
        self.board_height = 0
        self.board_width = 0
        self.vehicles = []
        self.walls = []
        self.board = []

    def setVehicles(self, filename):
        """Load vehicles and board size (and walls if any) from a CSV file"""
        with open(filename, newline="") as f:
            reader = csv.reader(f)
            lines = list(reader)

        # First line = board dimensions
        self.board_height, self.board_width = map(int, lines[0])

        # Reset vehicles and walls
        self.vehicles = []
        self.walls = []

        # Load each line
        for line in lines[1:]:
            if line[0] == "#":
                # It's a wall (format: #,x,y)
                x, y = int(line[1]), int(line[2])
                self.walls.append((y, x))  # store as (row, col)
            else:
                # It's a vehicle
                vid, x, y, orientation, length = line
                self.vehicles.append(Vehicle(vid, x, y, orientation, length))

    def setBoard(self):
        """Generate the game board from vehicles and walls"""
        self.board = [["." for _ in range(self.board_width)] for _ in range(self.board_height)]

        # Place vehicles
        for v in self.vehicles:
            if v.orientation == "H":
                for i in range(v.length):
                    self.board[v.row][v.col + i] = v.vid
            else:  # Vertical
                for i in range(v.length):
                    self.board[v.row + i][v.col] = v.vid

        # Place walls
        for (r, c) in self.walls:
            self.board[r][c] = "#"

    def display(self):
        """Print the board nicely"""
        for row in self.board:
            print(" ".join(row))
        print()

    def isGoal(self):
        """
        Check if the red car 'X' has reached the goal position:
        the right edge of the board (exit).
        """
        for v in self.vehicles:
            if v.vid == "X":
                # For horizontal red car, check if its front is at the exit
                if v.orientation == "H":
                    # The red car is goal when its front is at the last column - 1
                    if v.col + v.length - 1 == self.board_width - 1:
                        return True
        return False

    def successorFunction(self):
        """
        Generate all possible moves (action, successor_state)
        - Each action is a tuple (vehicle_id, direction)
        - Each successor_state is a new RushHourPuzzle object
        """
        successors = []

        for v in self.vehicles:
            # Horizontal vehicle
            if v.orientation == "H":
                # Move left
                if v.col > 0 and self.board[v.row][v.col - 1] == ".":
                    new_state = self._copy_state()
                    new_state._moveVehicle(v.vid, -1)
                    successors.append(((v.vid, "L"), new_state))

                # Move right
                if v.col + v.length < self.board_width and self.board[v.row][v.col + v.length] == ".":
                    new_state = self._copy_state()
                    new_state._moveVehicle(v.vid, 1)
                    successors.append(((v.vid, "R"), new_state))

            # Vertical vehicle
            else:
                # Move up
                if v.row > 0 and self.board[v.row - 1][v.col] == ".":
                    new_state = self._copy_state()
                    new_state._moveVehicle(v.vid, -1)
                    successors.append(((v.vid, "U"), new_state))

                # Move down
                if v.row + v.length < self.board_height and self.board[v.row + v.length][v.col] == ".":
                    new_state = self._copy_state()
                    new_state._moveVehicle(v.vid, 1)
                    successors.append(((v.vid, "D"), new_state))

        return successors

    def _copy_state(self):
        """Return a deep copy of the current puzzle state"""
        new_puzzle = RushHourPuzzle()
        new_puzzle.board_height = self.board_height
        new_puzzle.board_width = self.board_width
        new_puzzle.vehicles = [Vehicle(v.vid, v.col, v.row, v.orientation, v.length) for v in self.vehicles]
        new_puzzle.walls = list(self.walls)
        new_puzzle.setBoard()
        return new_puzzle

    def _moveVehicle(self, vid, step):
        """Move a vehicle left/right/up/down depending on its orientation"""
        for v in self.vehicles:
            if v.vid == vid:
                if v.orientation == "H":
                    v.col += step
                else:
                    v.row += step
                break
        self.setBoard()

class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state          # RushHourPuzzle instance
        self.parent = parent        # Parent Node
        self.action = action        # (vehicle_id, direction) that led to this state
        self.path_cost = path_cost  # Cost so far (number of moves)

    def getPath(self):
        """Return the sequence of states from initial to current node"""
        node, path = self, []
        while node:
            path.append(node.state)
            node = node.parent
        return list(reversed(path))

    def getSolution(self):
        """Return the sequence of actions taken to reach this node from initial"""
        node, actions = self, []
        while node and node.action:
            actions.append(node.action)
            node = node.parent
        return list(reversed(actions))

def bfs(initial_puzzle):
    """Breadth-First Search algorithm to solve Rush Hour puzzle"""
    root = Node(initial_puzzle)
    if root.state.isGoal():
        return root  # Already solved

    frontier = deque([root])
    explored = set()

    def state_hash(puzzle):
        """Create a hashable representation of the puzzle state for visited check"""
        # Use vehicle positions and orientations as a tuple key
        return tuple((v.vid, v.row, v.col, v.orientation, v.length) for v in sorted(puzzle.vehicles, key=lambda x: x.vid))

    explored.add(state_hash(root.state))

    while frontier:
        node = frontier.popleft()
        for action, successor_state in node.state.successorFunction():
            h = state_hash(successor_state)
            if h not in explored:
                child = Node(successor_state, parent=node, action=action, path_cost=node.path_cost + 1)
                if child.state.isGoal():
                    return child
                frontier.append(child)
                explored.add(h)

    return None  # No solution found

# =============================
# Test the puzzle with CSV file
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
    successors = puzzle.successorFunction() 
    puzzle.display()

    print("Is goal?", puzzle.isGoal())

    solution_node = bfs(puzzle)
    if solution_node:
        animate_solution_with_original(puzzle, solution_node)
        print("Solution found in", solution_node.path_cost, "steps")
        print("Actions to solve:")
        for action in solution_node.getSolution():
            print(action)
    else:
        print("No solution found")