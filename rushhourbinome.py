import csv
from collections import deque
import time
import heapq
import pygame  # type: ignore
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 650
BOARD_MARGIN = 50
INFO_PANEL_WIDTH = 400
CELL_SIZE = 60
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (100, 100, 100)

# Vehicle colors with realistic car colors
VEHICLE_COLORS = {
    'X': ((255, 0, 0), (180, 0, 0)),  # red 
    'A': ((0, 0, 255), (0, 0, 180)),  # Royal Blue
    'B': ((30, 144, 255), (20, 100, 200)),  # Dodger Blue
    'C': ((0, 191, 255), (0, 140, 200)),  # Deep Sky Blue
    'D': ((100, 149, 237), (70, 100, 200)),  # Cornflower Blue
    'E': ((65, 105, 225), (45, 75, 180)),  # Royal Blue
    'F': ((0, 0, 139), (0, 0, 100)),  # Dark Blue
    'G': ((72, 61, 139), (50, 40, 100)),  # Dark Slate Blue
    'H': ((106, 90, 205), (80, 60, 160)),  # Slate Blue
    'I': ((123, 104, 238), (90, 70, 180)),  # Medium Slate Blue
    'J': ((135, 206, 250), (100, 150, 200)),  # Light Sky Blue
}

class Vehicle:
    def __init__(self, vid, x, y, orientation, length):
        self.vid = vid
        self.row = int(y)              
        self.col = int(x)              
        self.orientation = orientation 
        self.length = int(length)

    def __repr__(self):
        return f"Vehicle({self.vid}, {self.col}, {self.row}, {self.orientation}, {self.length})"


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
        for row in self.board:
            print(" ".join(row))
        print()

    def isGoal(self):
        # Find the red car
        red_car = None
        for v in self.vehicles:
            if v.vid == 'X':
                red_car = v
                break
        
        if not red_car:
            return False
        
        if red_car.orientation == "H":
            # Check if front of red car is at the rightmost column
            return red_car.col + red_car.length == self.board_width
        return False

    def successorFunction(self):
        successors = []
        
        # Create a temporary board for collision detection
        temp_board = [["." for _ in range(self.board_width)] for _ in range(self.board_height)]
        
        # Place walls on temp board
        for (r, c) in self.walls:
            temp_board[r][c] = "#"
            
        # Place vehicles on temp board
        for v in self.vehicles:
            if v.orientation == "H":
                for i in range(v.length):
                    temp_board[v.row][v.col + i] = v.vid
            else:  # Vertical
                for i in range(v.length):
                    temp_board[v.row + i][v.col] = v.vid
        
        # Try to move each vehicle
        for idx, vehicle in enumerate(self.vehicles):
            # Try moving left/up (negative direction)
            for move_amount in range(1, self.board_width if vehicle.orientation == "H" else self.board_height):
                new_col = vehicle.col - move_amount if vehicle.orientation == "H" else vehicle.col
                new_row = vehicle.row - move_amount if vehicle.orientation == "V" else vehicle.row
                
                # Check if move is valid
                if self._isValidMove(vehicle, new_row, new_col, temp_board):
                    # Create new state
                    new_puzzle = self._createSuccessorState(idx, new_row, new_col)
                    direction = 'left' if vehicle.orientation == 'H' else 'up'
                    action = f"Move {vehicle.vid} {direction} {move_amount}"
                    successors.append((action, new_puzzle))
                else:
                    break  # Can't move further in this direction
            
            # Try moving right/down (positive direction)
            for move_amount in range(1, self.board_width if vehicle.orientation == "H" else self.board_height):
                new_col = vehicle.col + move_amount if vehicle.orientation == "H" else vehicle.col
                new_row = vehicle.row + move_amount if vehicle.orientation == "V" else vehicle.row
                
                # Check if move is valid
                if self._isValidMove(vehicle, new_row, new_col, temp_board):
                    # Create new state
                    new_puzzle = self._createSuccessorState(idx, new_row, new_col)
                    direction = 'right' if vehicle.orientation == 'H' else 'down'
                    action = f"Move {vehicle.vid} {direction} {move_amount}"
                    successors.append((action, new_puzzle))
                else:
                    break  # Can't move further in this direction
        
        return successors

    def _isValidMove(self, vehicle, new_row, new_col, board):
        if vehicle.orientation == "H":
            # Check horizontal bounds
            if new_col < 0 or new_col + vehicle.length > self.board_width:
                return False
            
            # Check for collisions along the new position
            for i in range(vehicle.length):
                cell_content = board[vehicle.row][new_col + i]
                if cell_content not in [".", vehicle.vid]:
                    return False
        else:  # Vertical
            # Check vertical bounds
            if new_row < 0 or new_row + vehicle.length > self.board_height:
                return False
            
            # Check for collisions along the new position
            for i in range(vehicle.length):
                cell_content = board[new_row + i][vehicle.col]
                if cell_content not in [".", vehicle.vid]:
                    return False
        
        return True

    def _createSuccessorState(self, vehicle_idx, new_row, new_col):
        new_puzzle = RushHourPuzzle()
        new_puzzle.board_height = self.board_height
        new_puzzle.board_width = self.board_width
        new_puzzle.walls = self.walls.copy()
        
        # Copy all vehicles
        new_puzzle.vehicles = []
        for i, v in enumerate(self.vehicles):
            if i == vehicle_idx:
                # Create moved vehicle
                new_vehicle = Vehicle(v.vid, new_col, new_row, v.orientation, v.length)
                new_puzzle.vehicles.append(new_vehicle)
            else:
                # Copy original vehicle
                new_vehicle = Vehicle(v.vid, v.col, v.row, v.orientation, v.length)
                new_puzzle.vehicles.append(new_vehicle)
        
        # Regenerate board
        new_puzzle.setBoard()
        return new_puzzle

    def __eq__(self, other):
        if not isinstance(other, RushHourPuzzle):
            return False
        
        # Check if vehicles are in the same positions
        if len(self.vehicles) != len(other.vehicles):
            return False
        
        for v1, v2 in zip(self.vehicles, other.vehicles):
            if (v1.vid != v2.vid or v1.row != v2.row or v1.col != v2.col or 
                v1.orientation != v2.orientation or v1.length != v2.length):
                return False
        
        return True

    def __hash__(self):
        # Create a hash based on vehicle positions
        vehicle_data = []
        for v in sorted(self.vehicles, key=lambda x: x.vid):
            vehicle_data.append((v.vid, v.row, v.col, v.orientation, v.length))
        return hash(tuple(vehicle_data))


class Node:
    def __init__(self, state, parent=None, action=None, g=0, f=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.f = f
    
    def getPath(self):
        path = []
        current = self
        while current is not None:
            path.append(current.state)
            current = current.parent
        path.reverse()
        return path
    
    def getSolution(self):
        actions = []
        current = self
        while current.parent is not None:
            actions.append(current.action)
            current = current.parent
        actions.reverse()
        return actions
    
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.state == other.state
    
    def __hash__(self):
        return hash(self.state)
    
    def __lt__(self, other):
        # For priority queue comparison
        return self.f < other.f


def BFS(s, successorsFn, isGoal):
    start_time = time.time()
    
    Open = deque()
    Closed = set()
    
    init_node = Node(s, None, None)
    
    if isGoal(init_node.state):
        end_time = time.time()
        return init_node, end_time - start_time
    
    Open.append(init_node)
    Closed = set()
    
    
    while Open:
        
        current = Open.popleft()
        
        Closed.add(current.state)
        
        for action, successor in successorsFn(current.state):
            child = Node(successor, current, action, 0)
            
            # First check if this child is the goal state
            if isGoal(child.state):
                end_time = time.time()
                return child, end_time - start_time
            
            # Then check if we should add it to Open
            if child.state not in Closed and not any(node.state == child.state for node in Open):
                Open.append(child)
    
    end_time = time.time()
    return None, end_time - start_time


def AStar(s, successorsFn, isGoal, h):
    start_time = time.time()
    
    Open = []
    Closed = set()
    
    # Initialize the start node
    init_node = Node(s, None, None)
    init_node.g = 0
    init_node.f = h(init_node)
    
    heapq.heappush(Open, (init_node.f, init_node))
    
    while Open:
        # Get node with lowest f value
        current_f, current = heapq.heappop(Open)
        
        # Skip if this state was already expanded
        if current.state in Closed:
            continue
            
        if isGoal(current.state):
            end_time = time.time()
            return current, end_time - start_time
        
        Closed.add(current.state)
        
        for action, successor in successorsFn(current.state):
            child_state = successor
            
            # Skip if already expanded
            if child_state in Closed:
                continue
                
            child_g = current.g + 1
            child_f = child_g + h(Node(child_state, None, None, child_g, 0))
            
            # Create child node and add to Open
            child_node = Node(child_state, current, action, child_g, child_f)
            heapq.heappush(Open, (child_f, child_node))
    
    end_time = time.time()
    return None, end_time - start_time


# Heuristic functions
def h1(node):
    state = node.state
    red_car = None
    
    # Find the red car
    for v in state.vehicles:
        if v.vid == 'X':
            red_car = v
            break
    
    if not red_car or red_car.orientation != "H":
        return float('inf')
    
    # Distance from the front of the red car to the right edge
    distance = state.board_width - (red_car.col + red_car.length)
    return distance

def h2(node):
    state = node.state
    red_car = None
    
    # Find the red car
    for v in state.vehicles:
        if v.vid == 'X':
            red_car = v
            break
    
    if not red_car or red_car.orientation != "H":
        return float('inf')
    
    # Calculate h1
    h1_value = state.board_width - (red_car.col + red_car.length)
    
    # Count vehicles blocking the path
    blocking_count = 0
    red_car_row = red_car.row
    red_car_front_col = red_car.col + red_car.length
    
    # Check each column from the red car's front to the exit
    for col in range(red_car_front_col, state.board_width):
        cell_content = state.board[red_car_row][col]
        if cell_content != '.' and cell_content != 'X':
            blocking_count += 1
    
    return h1_value + blocking_count

def h3(node):
    # take in considiration : The distance to exit like h1, The number of blocking vehicles like h2,The minimum number of moves needed to clear 
   # each blocking vehicle
    
    state = node.state
    red_car = None
    
    # Find the red car
    for v in state.vehicles:
        if v.vid == 'X':
            red_car = v
            break
    
    if not red_car or red_car.orientation != "H":
        return float('inf')
    
    # Calculate h1
    h1_value = state.board_width - (red_car.col + red_car.length)
    
    # Count vehicles blocking the path and estimate moves to clear them
    total_blocking_cost = 0
    red_car_row = red_car.row
    red_car_front_col = red_car.col + red_car.length
    
    blocking_vehicles = set()
    
    # First pass: identify all blocking vehicles
    for col in range(red_car_front_col, state.board_width):
        cell_content = state.board[red_car_row][col]
        if cell_content != '.' and cell_content != 'X' and cell_content not in blocking_vehicles:
            blocking_vehicles.add(cell_content)
    
    # For each blocking vehicle, estimate minimum moves to clear it
    for vid in blocking_vehicles:
        blocking_vehicle = None
        for v in state.vehicles:
            if v.vid == vid:
                blocking_vehicle = v
                break
        
        if not blocking_vehicle:
            continue
            
        if blocking_vehicle.orientation == "H":
            # Horizontal vehicles can't be on the same row as red car and block it
            # This shouldn't happen in valid states
            total_blocking_cost += 2  # Conservative estimate
        else:
            # Vertical vehicle blocking the path
            # Minimum moves to clear: need to move it up or down
            # Check available space above and below
            
            space_above = 0
            space_below = 0
            
            # Check space above
            for r in range(blocking_vehicle.row - 1, -1, -1):
                if state.board[r][blocking_vehicle.col] == '.':
                    space_above += 1
                else:
                    break
            
            # Check space below  
            for r in range(blocking_vehicle.row + blocking_vehicle.length, state.board_height):
                if state.board[r][blocking_vehicle.col] == '.':
                    space_below += 1
                else:
                    break
            
            # Minimum moves needed: at least 1 to move, plus potentially more if space is limited
            min_moves = 1
            if space_above == 0 and space_below == 0:
                # Vehicle is completely blocked, will need multiple moves to clear
                min_moves = 3  # Conservative estimate
            elif space_above < blocking_vehicle.length and space_below < blocking_vehicle.length:
                # Limited space in both directions
                min_moves = 2
            
            total_blocking_cost += min_moves
    
    return h1_value + total_blocking_cost


class PygameVisualizer:
    def __init__(self, puzzle):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Rush Hour Puzzle Solver")
        self.clock = pygame.time.Clock()

        # Initialize fonts with Times New Roman
        self.font = pygame.font.SysFont("Times New Roman", 36)
        self.small_font = pygame.font.SysFont("Times New Roman", 24)
   
        self.puzzle = puzzle
        
        # Create default colors for vehicles not in VEHICLE_COLORS
        self.default_colors = [(100, 100, 200), (200, 100, 100), (100, 200, 100), 
                              (200, 200, 100), (200, 100, 200), (100, 200, 200)]
        self.default_color_index = 0
    
    def draw_realistic_car(self, surface, rect, orientation, color_pair, vid):
        #draw a more realistic car
        main_color, dark_color = color_pair
        
        # Draw car body with rounded corners
        if orientation == "H":
            # Horizontal car - longer body
            body_rect = pygame.Rect(rect.x, rect.y + 5, rect.width, rect.height - 10)
        else:
            # Vertical car - taller body
            body_rect = pygame.Rect(rect.x + 5, rect.y, rect.width - 10, rect.height)
        
        # Draw main car body with gradient effect
        pygame.draw.rect(surface, main_color, body_rect, border_radius=8)
        
        # Draw car top (for 3D effect)
        if orientation == "H":
            top_rect = pygame.Rect(rect.x + 5, rect.y + 8, rect.width - 10, 8)
        else:
            top_rect = pygame.Rect(rect.x + 8, rect.y + 5, 8, rect.height - 10)
        
        pygame.draw.rect(surface, dark_color, top_rect, border_radius=4)
        
        # Draw wheels
        wheel_radius = 6
        if orientation == "H":
            # Front and back wheels for horizontal cars
            pygame.draw.circle(surface, BLACK, (rect.x + 15, rect.y + rect.height - 8), wheel_radius)
            pygame.draw.circle(surface, BLACK, (rect.x + rect.width - 15, rect.y + rect.height - 8), wheel_radius)
            pygame.draw.circle(surface, BLACK, (rect.x + 15, rect.y + 8), wheel_radius)
            pygame.draw.circle(surface, BLACK, (rect.x + rect.width - 15, rect.y + 8), wheel_radius)
            
            # Add wheel highlights
            pygame.draw.circle(surface, DARK_GRAY, (rect.x + 15, rect.y + rect.height - 8), wheel_radius - 2)
            pygame.draw.circle(surface, DARK_GRAY, (rect.x + rect.width - 15, rect.y + rect.height - 8), wheel_radius - 2)
            pygame.draw.circle(surface, DARK_GRAY, (rect.x + 15, rect.y + 8), wheel_radius - 2)
            pygame.draw.circle(surface, DARK_GRAY, (rect.x + rect.width - 15, rect.y + 8), wheel_radius - 2)
        else:
            # Front and back wheels for vertical cars
            pygame.draw.circle(surface, BLACK, (rect.x + 8, rect.y + 15), wheel_radius)
            pygame.draw.circle(surface, BLACK, (rect.x + 8, rect.y + rect.height - 15), wheel_radius)
            pygame.draw.circle(surface, BLACK, (rect.x + rect.width - 8, rect.y + 15), wheel_radius)
            pygame.draw.circle(surface, BLACK, (rect.x + rect.width - 8, rect.y + rect.height - 15), wheel_radius)
            
            # Add wheel highlights
            pygame.draw.circle(surface, DARK_GRAY, (rect.x + 8, rect.y + 15), wheel_radius - 2)
            pygame.draw.circle(surface, DARK_GRAY, (rect.x + 8, rect.y + rect.height - 15), wheel_radius - 2)
            pygame.draw.circle(surface, DARK_GRAY, (rect.x + rect.width - 8, rect.y + 15), wheel_radius - 2)
            pygame.draw.circle(surface, DARK_GRAY, (rect.x + rect.width - 8, rect.y + rect.height - 15), wheel_radius - 2)
        
        # Draw windows
        window_color = (200, 230, 255)
        if orientation == "H":
            if rect.width > CELL_SIZE * 1.5:  # Only draw windows for longer cars
                window_rect1 = pygame.Rect(rect.x + 20, rect.y + 12, 15, 8)
                window_rect2 = pygame.Rect(rect.x + rect.width - 35, rect.y + 12, 15, 8)
                pygame.draw.rect(surface, window_color, window_rect1, border_radius=2)
                pygame.draw.rect(surface, window_color, window_rect2, border_radius=2)
        else:
            if rect.height > CELL_SIZE * 1.5:  # Only draw windows for taller cars
                window_rect1 = pygame.Rect(rect.x + 12, rect.y + 20, 8, 15)
                window_rect2 = pygame.Rect(rect.x + 12, rect.y + rect.height - 35, 8, 15)
                pygame.draw.rect(surface, window_color, window_rect1, border_radius=2)
                pygame.draw.rect(surface, window_color, window_rect2, border_radius=2)
        
        # Draw license plate/vehicle ID
        plate_color = (230, 230, 230)
        if orientation == "H":
            plate_rect = pygame.Rect(rect.x + rect.width//2 - 15, rect.y + rect.height - 18, 30, 10)
        else:
            plate_rect = pygame.Rect(rect.x + rect.width - 18, rect.y + rect.height//2 - 15, 10, 30)
        
        pygame.draw.rect(surface, plate_color, plate_rect, border_radius=2)
        
        # Draw vehicle ID on plate
        text = self.small_font.render(vid, True, BLACK)
        if orientation == "H":
            text_rect = text.get_rect(center=plate_rect.center)
        else:
            # Rotate text for vertical cars
            text = pygame.transform.rotate(text, 90)
            text_rect = text.get_rect(center=plate_rect.center)
        
        surface.blit(text, text_rect)
        
        # Add car outline
        pygame.draw.rect(surface, BLACK, body_rect, 2, border_radius=8)
    
    def draw_board(self, state, current_step, total_steps, algorithm_name, stats):
        self.screen.fill(WHITE)
        
        # Draw info panel
        self.draw_info_panel(current_step, total_steps, algorithm_name, stats)
        
        # Calculate board position
        board_width_px = state.board_width * CELL_SIZE
        board_height_px = state.board_height * CELL_SIZE
        board_x = BOARD_MARGIN
        board_y = (SCREEN_HEIGHT - board_height_px) // 2
        
        # Draw board background (asphalt-like)
        asphalt_color = (80, 80, 80)
        pygame.draw.rect(self.screen, asphalt_color, (board_x, board_y, board_width_px, board_height_px))
        
        # Draw road markings (yellow lines)
        line_color = (255, 255, 0)
        line_width = 2
        
        # Horizontal center line
        center_y = board_y + board_height_px // 2
        pygame.draw.line(self.screen, line_color, 
                        (board_x, center_y),
                        (board_x + board_width_px, center_y), line_width)
        
        # Vertical center line (dashed)
        center_x = board_x + board_width_px // 2
        for y in range(board_y, board_y + board_height_px, 20):
            if (y - board_y) % 40 < 20:
                pygame.draw.line(self.screen, line_color,
                               (center_x, y),
                               (center_x, min(y + 10, board_y + board_height_px)), line_width)
        
        # Draw grid lines (white road markings)
        for row in range(state.board_height + 1):
            y = board_y + row * CELL_SIZE
            pygame.draw.line(self.screen, WHITE, 
                           (board_x, y),
                           (board_x + board_width_px, y), 1)
        
        for col in range(state.board_width + 1):
            x = board_x + col * CELL_SIZE
            pygame.draw.line(self.screen, WHITE,
                           (x, board_y),
                           (x, board_y + board_height_px), 1)
        
        # Draw exit (as a garage door)
        exit_y = board_y + 2 * CELL_SIZE
        exit_rect = pygame.Rect(
            board_x + state.board_width * CELL_SIZE, 
            exit_y, 
            15, 
            CELL_SIZE
        )
        # Draw garage door
        pygame.draw.rect(self.screen, (0, 0, 0), exit_rect)  
        # Draw door panels
        for i in range(3):
            panel_rect = pygame.Rect(
                exit_rect.x,
                exit_rect.y + i * (CELL_SIZE // 3),
                exit_rect.width,
                CELL_SIZE // 3 - 2
            )
            pygame.draw.rect(self.screen, (180, 90, 0), panel_rect)
        
        # Draw walls (as buildings/obstacles)
        for wall_row, wall_col in state.walls:
            wall_rect = pygame.Rect(
                board_x + wall_col * CELL_SIZE,
                board_y + wall_row * CELL_SIZE,
                CELL_SIZE, CELL_SIZE
            )
            # Draw building-like wall
            pygame.draw.rect(self.screen, (120, 120, 120), wall_rect)  # Gray building
            # Add building details
            pygame.draw.rect(self.screen, (100, 100, 100), wall_rect, 2)  # Outline
            # Add windows to building
            for i in range(2):
                for j in range(2):
                    window_rect = pygame.Rect(
                        wall_rect.x + 10 + i * 20,
                        wall_rect.y + 10 + j * 20,
                        12, 12
                    )
                    pygame.draw.rect(self.screen, (200, 230, 255), window_rect)  # Blue windows
        
        # Draw vehicles as realistic cars
        for vehicle in state.vehicles:
            # Get colors for this vehicle
            if vehicle.vid in VEHICLE_COLORS:
                color_pair = VEHICLE_COLORS[vehicle.vid]
            else:
                # Use default color if not specified
                color_pair = (self.default_colors[self.default_color_index % len(self.default_colors)], 
                             (50, 50, 100))
                self.default_color_index += 1
            
            if vehicle.orientation == "H":
                # Horizontal vehicle
                vehicle_rect = pygame.Rect(
                    board_x + vehicle.col * CELL_SIZE + 2,
                    board_y + vehicle.row * CELL_SIZE + 2,
                    vehicle.length * CELL_SIZE - 4,
                    CELL_SIZE - 4
                )
            else:
                # Vertical vehicle
                vehicle_rect = pygame.Rect(
                    board_x + vehicle.col * CELL_SIZE + 2,
                    board_y + vehicle.row * CELL_SIZE + 2,
                    CELL_SIZE - 4,
                    vehicle.length * CELL_SIZE - 4
                )
            
            # Draw realistic car
            self.draw_realistic_car(self.screen, vehicle_rect, vehicle.orientation, color_pair, vehicle.vid)
        
        # Draw step counter on board
        step_text = self.font.render(f"Step: {current_step}/{total_steps}", True, WHITE)
        self.screen.blit(step_text, (board_x, board_y - 40))
        
        # Draw algorithm name above board
        algo_text = self.font.render(f"Algorithm: {algorithm_name}", True, (0, 0, 180))
        self.screen.blit(algo_text, (board_x, board_y - 70))
    
    def draw_info_panel(self, current_step, total_steps, algorithm_name, stats):
        panel_x = SCREEN_WIDTH - INFO_PANEL_WIDTH + 30
        panel_y = 50
        
        # Draw panel background (car dashboard style)
        dashboard_color = (0, 0, 180)
        pygame.draw.rect(self.screen, dashboard_color, 
                        (SCREEN_WIDTH - INFO_PANEL_WIDTH, 0, INFO_PANEL_WIDTH, SCREEN_HEIGHT))
        
        # Draw panel border
        pygame.draw.rect(self.screen, (0, 0, 180), 
                        (SCREEN_WIDTH - INFO_PANEL_WIDTH, 0, INFO_PANEL_WIDTH, SCREEN_HEIGHT), 3)
        
        # Title (like a car display)
        title = self.font.render("RUSH HOUR SOLVER", True, (173, 216, 230))  # light blue text
        self.screen.blit(title, (panel_x, panel_y))
        
        # Algorithm info
        algo_text = self.small_font.render(f"Algorithm: {algorithm_name}", True, WHITE)
        self.screen.blit(algo_text, (panel_x, panel_y + 50))
        
        step_text = self.small_font.render(f"Step: {current_step} / {total_steps}", True, WHITE)
        self.screen.blit(step_text, (panel_x, panel_y + 80))
        
        # Statistics panel
        stats_y = panel_y + 120
        stats_title = self.small_font.render("PERFORMANCE STATS:", True, (173, 216, 230))
        self.screen.blit(stats_title, (panel_x, stats_y))
        
        # Draw stats as gauges
        for i, (key, value) in enumerate(stats.items()):
            y_pos = stats_y + 30 + i * 25
            stat_text = self.small_font.render(f"{key}: {value}", True, WHITE)
            self.screen.blit(stat_text, (panel_x, y_pos))
            
            # Add a small indicator dot for visual appeal
            pygame.draw.circle(self.screen, (0, 255, 0), (panel_x - 10, y_pos + 8), 4)
        
        # Controls panel
        controls_y = SCREEN_HEIGHT - 180
        controls_title = self.small_font.render("CONTROLS:", True, (173, 216, 230))
        self.screen.blit(controls_title, (panel_x, controls_y))
        
        controls = [
            "SPACE: Play/Pause",
            "RIGHT: Next step", 
            "LEFT: Previous step",
            "R: Reset animation",
            "ESC: Quit simulation"
        ]
        
        for i, control in enumerate(controls):
            control_text = self.small_font.render(control, True, WHITE)
            self.screen.blit(control_text, (panel_x, controls_y + 30 + i * 25))
            
            # Add car icon next to controls
            car_icon_rect = pygame.Rect(panel_x - 25, controls_y + 25 + i * 25, 20, 10)
            pygame.draw.rect(self.screen, (173, 216, 230), car_icon_rect, border_radius=3)
    
    def animate_solution(self, solution_node, algorithm_name, stats, delay=500):
        if not solution_node:
            print(f"No solution to animate for {algorithm_name}")
            return
        
        path = solution_node.getPath()
        actions = solution_node.getSolution()
        
        current_step = 0
        paused = False
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_RIGHT and paused:
                        current_step = min(current_step + 1, len(actions))
                    elif event.key == pygame.K_LEFT and paused:
                        current_step = max(current_step - 1, 0)
                    elif event.key == pygame.K_r:
                        current_step = 0
            
            if not paused:
                current_step = (current_step + 1) % (len(actions) + 1)
                pygame.time.delay(delay)
            
            # Draw current state
            current_state = path[current_step] if current_step < len(path) else path[-1]
            action = actions[current_step - 1] if current_step > 0 else "Initial State"
            
            stats["Current Action"] = action
            self.draw_board(current_state, current_step, len(actions), algorithm_name, stats)
            
            # Check if goal is reached
            if current_step == len(actions):
                goal_text = self.font.render("GOAL REACHED! 🏁", True, (128, 0, 128))
                text_rect = goal_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
                self.screen.blit(goal_text, text_rect)
                
                # Draw celebration effect
                for i in range(5):
                    x = SCREEN_WIDTH // 2 - 100 + i * 50
                    pygame.draw.circle(self.screen, (128, 0, 128), (x, SCREEN_HEIGHT - 80), 8)
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
            # Auto-advance to next algorithm when solution completes
            if not paused and current_step == len(actions):
                pygame.time.delay(3000)  # Pause at goal for 3 seconds
                break


def solve_with_all_algorithms(puzzle):
    #solve the puzzle with all algorithms and return solutions with stats
    solutions = {}
    
    print("Solving with BFS...")
    bfs_solution, bfs_time = BFS(
        puzzle, lambda state: state.successorFunction(), lambda state: state.isGoal()
    )
    
    if bfs_solution:
        solutions["BFS"] = {
            "solution": bfs_solution,
            "stats": {
                "Execution Time": f"{bfs_time:.4f}s",
                "Solution Cost": len(bfs_solution.getSolution())
            }
        }
    
    # Test A* with different heuristics
    heuristics = [("A* (h1)", h1), ("A* (h2)", h2), ("A* (h3)", h3)]
    
    for h_name, h_func in heuristics:
        print(f"Solving with {h_name}...")
        a_star_solution, a_star_time = AStar(
            puzzle, lambda state: state.successorFunction(), lambda state: state.isGoal(), h_func
        )
        
        if a_star_solution:
            solutions[h_name] = {
                "solution": a_star_solution,
                "stats": {
                    "Execution Time": f"{a_star_time:.4f}s",
                    "Solution Cost": len(a_star_solution.getSolution())
                }
            }
    
    return solutions


def main():
    # Load puzzle
    puzzle = RushHourPuzzle()
    puzzle.setVehicles("1.csv")   # first CSV
    # puzzle.setVehicles("2-a.csv") # second CSV
    # puzzle.setVehicles("2-b.csv") # third CSV with wall
    # puzzle.setVehicles("2-c.csv") # fourth CSV with wall
    # puzzle.setVehicles("2-d.csv") # fifth CSV with wall
    # puzzle.setVehicles("2-e.csv") # sixth CSV with wall
    # puzzle.setVehicles("e-f.csv")   # seventh CSV 
    puzzle.setBoard()
    
    # Solve with all algorithms
    print("Solving puzzle with all algorithms...")
    solutions = solve_with_all_algorithms(puzzle)
    
    if not solutions:
        print("No solutions found!")
        return
    
    # Initialize visualizer
    visualizer = PygameVisualizer(puzzle)
    
    # Animate each solution
    for algorithm_name, solution_data in solutions.items():
        print(f"Animating {algorithm_name} solution...")
        visualizer.animate_solution(
            solution_data["solution"],
            algorithm_name,
            solution_data["stats"],
            delay=800  # milliseconds between steps
        )
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()