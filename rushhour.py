import csv

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


# =============================
# Test the puzzle with CSV file
# =============================

if __name__ == "__main__":
    puzzle = RushHourPuzzle()
    # puzzle.setVehicles("1.csv")   # first CSV
    # puzzle.setVehicles("2-a.csv") # second CSV
    #puzzle.setVehicles("2-b.csv")  # third CSV with wall
    #puzzle.setVehicles("2-c.csv")  # fourth CSV with wall
    #puzzle.setVehicles("2-d.csv")  # fifth CSV with wall
    #puzzle.setVehicles("2-e.csv")  # sixth CSV with wall
    puzzle.setVehicles("e-f.csv")   # seventh CSV with wall
    puzzle.setBoard()
    puzzle.display()
