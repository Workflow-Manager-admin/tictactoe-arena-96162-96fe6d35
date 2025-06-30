"""
Tic Tac Toe board logic/AI for handling moves, win/draw, board state, and simple AI policy.
"""


from typing import List, Optional, Tuple
import random

X = "X"
O_TOKEN = "O"
EMPTY = ""


# PUBLIC_INTERFACE
def initial_board() -> List[List[str]]:
    """Create initial 3x3 Tic Tac Toe board."""
    return [[EMPTY for _ in range(3)] for _ in range(3)]


# PUBLIC_INTERFACE
def check_winner(board: List[List[str]]) -> Optional[str]:
    """
    Return "X", "O" if there's a winner; else None.
    """
    # Rows, cols, diags
    for i in range(3):
        if all(board[i][j] == X for j in range(3)) or all(
            board[j][i] == X for j in range(3)
        ):
            return X
        if all(board[i][j] == O_TOKEN for j in range(3)) or all(
            board[j][i] == O_TOKEN for j in range(3)
        ):
            return O_TOKEN
    # Diagonals
    if all(board[i][i] == X for i in range(3)) or all(
        board[i][2 - i] == X for i in range(3)
    ):
        return X
    if all(board[i][i] == O_TOKEN for i in range(3)) or all(
        board[i][2 - i] == O_TOKEN for i in range(3)
    ):
        return O_TOKEN
    return None


# PUBLIC_INTERFACE
def is_draw(board: List[List[str]]) -> bool:
    """True if all cells filled and no winner."""
    for row in board:
        if EMPTY in row:
            return False
    return not check_winner(board)


# PUBLIC_INTERFACE
def valid_moves(board: List[List[str]]) -> List[Tuple[int, int]]:
    """Return list of empty cell (row, col) tuples."""
    return [(i, j) for i in range(3) for j in range(3) if board[i][j] == EMPTY]


# PUBLIC_INTERFACE
def make_move(board: List[List[str]], row: int, col: int, mark: str) -> List[List[str]]:
    """Safely place mark on board and return new board (does not mutate input)."""
    assert board[row][col] == EMPTY, "Invalid move"
    new_board = [r.copy() for r in board]
    new_board[row][col] = mark
    return new_board


# PUBLIC_INTERFACE
def ai_pick(board: List[List[str]]) -> Tuple[int, int]:
    """
    Naive AI: Picks a random available cell.
    """
    moves = valid_moves(board)
    if not moves:
        raise Exception("No valid moves left")
    return random.choice(moves)
