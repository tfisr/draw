"""
getui.py — 格推 (Getui) board game
A two-player 4×4 board game for children.

Rules summary
─────────────
Board  : 4×4 grid, 16 positions (row 0-3, col 0-3).
Pieces : Black (B) vs White (W).  Black moves first.
Phases :
  1. Placement phase  – while empty cells remain, each turn a player places
                        one piece on any empty cell, then any triggered
                        operations fire automatically.
  2. Abandonment phase – once the board is full, each turn a player either
                        removes one of their own pieces OR moves one of their
                        pieces one step (orthogonally), then operations fire.

Operations (fire automatically after every move, in order Push → Sandwich → Carry):
  Push (推)   : Two of YOUR pieces in a line, the very next cell(s) in that
                direction hold 1-2 ADJACENT enemy pieces → those enemies are
                removed.
  Sandwich (夹): Two of YOUR pieces in a line with exactly 1-2 adjacent enemy
                pieces between them → those enemies become YOUR pieces.
  Carry (担)  : One or two of YOUR pieces in a line flanked on BOTH ends by an
                enemy piece (patterns: E-Y-E, E-Y-Y-E) → those two enemy end
                pieces become YOUR pieces.

Win condition : After the abandonment phase begins, a player wins when the
               opponent has no pieces left on the board.
"""

from copy import deepcopy

EMPTY = "."
BLACK = "B"
WHITE = "W"
SIZE = 4

DIRECTIONS = [
    (0, 1),   # right
    (0, -1),  # left
    (1, 0),   # down
    (-1, 0),  # up
]


def make_board():
    return [[EMPTY] * SIZE for _ in range(SIZE)]


def opponent(player):
    return WHITE if player == BLACK else BLACK


def in_bounds(r, c):
    return 0 <= r < SIZE and 0 <= c < SIZE


def player_name(player):
    return "Black (B)" if player == BLACK else "White (W)"


def count_pieces(board, player):
    return sum(board[r][c] == player for r in range(SIZE) for c in range(SIZE))


def board_full(board):
    return all(board[r][c] != EMPTY for r in range(SIZE) for c in range(SIZE))


# ─── display ────────────────────────────────────────────────────────────────

def print_board(board):
    print()
    print("    " + "  ".join(str(c) for c in range(SIZE)))
    print("   " + "───" * SIZE)
    for r in range(SIZE):
        row_str = " | ".join(board[r][c] for c in range(SIZE))
        print(f" {r} | {row_str}")
    print()


# ─── operations ─────────────────────────────────────────────────────────────

def apply_push(board, player):
    """
    Push (推): two of YOUR pieces in a line → push away 1-2 adjacent enemies
    directly in front (in the direction YOUR two pieces point).
    Returns (new_board, changed: bool).
    """
    opp = opponent(player)
    changed = False
    new_board = deepcopy(board)

    for r in range(SIZE):
        for c in range(SIZE):
            if new_board[r][c] != player:
                continue
            for dr, dc in DIRECTIONS:
                r2, c2 = r + dr, c + dc
                if not in_bounds(r2, c2) or new_board[r2][c2] != player:
                    continue
                # two allied pieces at (r,c) and (r2,c2); enemies are AHEAD of (r2,c2)
                r3, c3 = r2 + dr, c2 + dc
                if not in_bounds(r3, c3) or new_board[r3][c3] != opp:
                    continue
                # at least one enemy ahead — remove 1 or 2
                new_board[r3][c3] = EMPTY
                changed = True
                r4, c4 = r3 + dr, c3 + dc
                if in_bounds(r4, c4) and new_board[r4][c4] == opp:
                    new_board[r4][c4] = EMPTY

    return new_board, changed


def apply_sandwich(board, player):
    """
    Sandwich (夹): two of YOUR pieces with 1-2 adjacent enemy pieces between
    them on the same line → enemies become YOUR pieces.
    Returns (new_board, changed: bool).
    """
    opp = opponent(player)
    changed = False
    new_board = deepcopy(board)

    for r in range(SIZE):
        for c in range(SIZE):
            if new_board[r][c] != player:
                continue
            for dr, dc in DIRECTIONS:
                # check gap of 1 enemy: Y E Y
                r2, c2 = r + dr, c + dc
                r3, c3 = r + 2 * dr, c + 2 * dc
                if (in_bounds(r2, c2) and in_bounds(r3, c3)
                        and new_board[r2][c2] == opp
                        and new_board[r3][c3] == player):
                    new_board[r2][c2] = player
                    changed = True

                # check gap of 2 enemies: Y E E Y
                r4, c4 = r + 3 * dr, c + 3 * dc
                if (in_bounds(r2, c2) and in_bounds(r3, c3) and in_bounds(r4, c4)
                        and new_board[r2][c2] == opp
                        and new_board[r3][c3] == opp
                        and new_board[r4][c4] == player):
                    new_board[r2][c2] = player
                    new_board[r3][c3] = player
                    changed = True

    return new_board, changed


def apply_carry(board, player):
    """
    Carry (担): enemy-your-enemy (E Y E) or enemy-your-your-enemy (E Y Y E)
    pattern on a line → the two enemy ends become YOUR pieces.
    Returns (new_board, changed: bool).
    """
    opp = opponent(player)
    changed = False
    new_board = deepcopy(board)

    for r in range(SIZE):
        for c in range(SIZE):
            for dr, dc in DIRECTIONS:
                # pattern E-Y-E (length 3)
                r0, c0 = r, c
                r1, c1 = r + dr, c + dc
                r2, c2 = r + 2 * dr, c + 2 * dc
                if (in_bounds(r0, c0) and in_bounds(r1, c1) and in_bounds(r2, c2)
                        and new_board[r0][c0] == opp
                        and new_board[r1][c1] == player
                        and new_board[r2][c2] == opp):
                    new_board[r0][c0] = player
                    new_board[r2][c2] = player
                    changed = True

                # pattern E-Y-Y-E (length 4)
                r3, c3 = r + 3 * dr, c + 3 * dc
                if (in_bounds(r0, c0) and in_bounds(r1, c1)
                        and in_bounds(r2, c2) and in_bounds(r3, c3)
                        and new_board[r0][c0] == opp
                        and new_board[r1][c1] == player
                        and new_board[r2][c2] == player
                        and new_board[r3][c3] == opp):
                    new_board[r0][c0] = player
                    new_board[r3][c3] = player
                    changed = True

    return new_board, changed


def apply_all_operations(board, player):
    """Run Push → Sandwich → Carry repeatedly until no more changes occur.

    The safety cap is SIZE * SIZE (16) because each iteration of the loop
    must convert or remove at least one piece to produce a change.  A 4×4
    board has at most 16 pieces, so the operations can cascade at most 16
    times before the board stabilises.
    """
    ops = [apply_push, apply_sandwich, apply_carry]
    op_names = ["Push (推)", "Sandwich (夹)", "Carry (担)"]
    any_fired = False
    for _ in range(SIZE * SIZE):          # safety cap
        fired_this_round = False
        for op, name in zip(ops, op_names):
            new_board, changed = op(board, player)
            if changed:
                board = new_board
                fired_this_round = True
                any_fired = True
                print(f"  → Operation fired: {name}")
        if not fired_this_round:
            break
    return board, any_fired


# ─── input helpers ──────────────────────────────────────────────────────────

def parse_coord(text):
    """Parse 'row col' or 'row,col' into (r, c) or raise ValueError."""
    text = text.strip().replace(",", " ")
    parts = text.split()
    if len(parts) != 2:
        raise ValueError
    r, c = int(parts[0]), int(parts[1])
    if not in_bounds(r, c):
        raise ValueError
    return r, c


def ask_coord(prompt):
    while True:
        try:
            return parse_coord(input(prompt))
        except (ValueError, IndexError):
            print("  Invalid input. Enter row and column (0-3), e.g. '1 2'.")


# ─── placement phase ────────────────────────────────────────────────────────

def placement_turn(board, player):
    print(f"\n{player_name(player)}'s turn — PLACEMENT PHASE")
    print_board(board)
    while True:
        r, c = ask_coord("  Place your piece (row col): ")
        if board[r][c] == EMPTY:
            board[r][c] = player
            break
        print("  That cell is occupied. Choose another.")
    board, _ = apply_all_operations(board, player)
    return board


# ─── abandonment phase ──────────────────────────────────────────────────────

def abandonment_turn(board, player):
    print(f"\n{player_name(player)}'s turn — ABANDONMENT PHASE")
    print_board(board)
    print("  Options:  R = remove one of your pieces")
    print("            M = move one of your pieces one step")
    while True:
        choice = input("  Your choice (R/M): ").strip().upper()
        if choice in ("R", "M"):
            break
        print("  Please enter R or M.")

    if choice == "R":
        while True:
            r, c = ask_coord("  Remove piece at (row col): ")
            if board[r][c] == player:
                board[r][c] = EMPTY
                break
            print("  That is not your piece.")
    else:  # move
        while True:
            r, c = ask_coord("  Move piece FROM (row col): ")
            if board[r][c] == player:
                break
            print("  That is not your piece.")
        while True:
            nr, nc = ask_coord("  Move piece TO   (row col): ")
            dr, dc = nr - r, nc - c
            if abs(dr) + abs(dc) == 1 and board[nr][nc] == EMPTY:
                board[nr][nc] = player
                board[r][c] = EMPTY
                break
            print("  Must move exactly one step orthogonally to an empty cell.")

    board, _ = apply_all_operations(board, player)
    return board


# ─── main game loop ─────────────────────────────────────────────────────────

def check_winner(board, abandonment_started):
    """Return the winner symbol, or None if the game continues."""
    if not abandonment_started:
        return None
    b = count_pieces(board, BLACK)
    w = count_pieces(board, WHITE)
    if b == 0:
        return WHITE
    if w == 0:
        return BLACK
    return None


def play():
    print("=" * 46)
    print("       格推 (Getui) — Children's Board Game")
    print("=" * 46)
    print("  4×4 board  |  Black (B) vs White (W)  |  Black first")
    print("  Operations fire automatically after each move.")
    print()

    board = make_board()
    current = BLACK
    abandonment_started = False

    while True:
        # check win
        winner = check_winner(board, abandonment_started)
        if winner is not None:
            print_board(board)
            print(f"  🎉  {player_name(winner)} wins!")
            break

        # switch phase if board just became full
        if board_full(board) and not abandonment_started:
            abandonment_started = True
            print("\n  *** Board is full — Abandonment Phase begins! ***")

        if not abandonment_started:
            board = placement_turn(board, current)
        else:
            board = abandonment_turn(board, current)

        # switch player
        current = opponent(current)


if __name__ == "__main__":
    play()
