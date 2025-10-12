# Rush Hour Puzzle Solver

This project models the classic **Rush Hour puzzle**.  
It reads puzzle configurations from CSV files and displays the board in text format and prepares for solving it using search algorithms.

## 📌 Project Structure
- `rushhour.py` → Python code that models the puzzle (board, vehicles, walls).
- `1.csv`, `2-a.csv`, `2-b.csv`, ... → Example puzzle configurations.
- Future steps → Implement other algorithms to solve the puzzle.

## 🚗 Puzzle Rules
- Vehicles are either horizontal or vertical.
- Cars occupy 2 spaces, trucks occupy 3 spaces.
- The red car **X** must reach the exit (right edge of the board).

Walls may also exist, marked by `#` in the CSV files.

## ▶️ How to Run
1. Make sure you have **Python 3** installed.
2. Run the program with:
   ```bash
   python rushhour.py
   
3. The program will display the initial puzzle board and then animate the solution moves to free the red car.

4. During animation:
   - The original puzzle remains displayed on top
   - The solution states are shown step-by-step below, with the red car colored red
   - The exit column is open where the red car exits
