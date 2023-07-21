"""Connect 4 implementation in python, command line."""
import random
import sys
import copy
import typing

class Board:
    def __init__(self, win_length: int = 4, width: int = 7, height: int = 6):
        self.board: list[list[str]] = [[] for _ in range(width)]
        self.history = ""
        self.width = width
        self.height = height
        self.win_length = win_length
        self.p1 = "□"
        self.p2 = "■"
        self.turn = self.p1
    def change_turn(self):
        self.turn = self.p2 if self.turn == self.p1 else self.p1
    def copy(self):
        new_board = Board(self.win_length, self.width, self.height)
        new_board.history = self.history
        new_board.board = copy.deepcopy(self.board)
        return new_board
    def in_width(self, pos: int) -> bool:
        return 0 <= pos < self.width
    def in_height(self, pos: int) -> bool:
        return len(self.board[pos]) < self.height
    def in_board(self, pos: int) -> bool:
        return self.in_width(pos) and self.in_height(pos)
    def insert_piece(self, pos: int, piece: str) -> bool:
        """Returns true if successful, false if not successful."""
        if self.in_board(pos):
            self.board[pos].append(piece)
            self.history += str(pos)
            return True
        else:
            return False
    def check_win_vertical(self, pos: int) -> bool:
        # If the column is less than win_length pieces high, it's not a win.
        if len(self.board[pos]) < self.win_length:
            return False
        # Iterate down the stack and check if the top 4 pieces are the same
        for i in range(self.win_length-1):
            if self.board[pos][-(i+2)] != self.board[pos][-1]:
                return False
        return True
    def check_win_horizontal(self, pos: int) -> bool:
        y = self.get_column_height(pos) - 1
        match_piece = self.get_top_piece(pos)
        # No pieces in pos column means no win
        if y < 0 or match_piece is None:
            return False
        leftmost_win = min(0, pos - self.win_length)
        rightmost_win = min(pos + self.win_length, self.width - 1)
        matching = 0
        for x in range(leftmost_win, rightmost_win + 1):
            if self.get_piece_at(x, y) == match_piece:
                matching += 1
            else:
                matching = 0
            if matching == self.win_length:
                return True
        return False
    
    def check_win_diagonals(self, pos: int) -> bool:
        y = self.get_column_height(pos) - 1
        match_piece = self.get_top_piece(pos)
        if y < 0 or match_piece is None:
            return False
        leftmost_win = min(0, pos - self.win_length)
        rightmost_win = min(pos + self.win_length, self.width - 1)
        # Top down diagonal
        td_matching = 0
        # Down up (down top) diagonal
        dt_matching = 0
        for x in range(leftmost_win, rightmost_win + 1):
            td_y = y + (pos - x)
            dt_y = y + (x - pos)
            if self.get_piece_at(x, td_y) == match_piece:
                td_matching += 1
            else:
                td_matching = 0
            if self.get_piece_at(x, dt_y) == match_piece:
                dt_matching += 1
            else:
                dt_matching = 0
            if dt_matching == self.win_length or td_matching == self.win_length:
                return True
        return False
    
    def check_win(self, pos: int) -> bool:
        # Check every vertical, horizonta, and diagonal passing through the position
        return self.check_win_vertical(pos) or \
               self.check_win_horizontal(pos) or \
               self.check_win_diagonals(pos)
    def is_full(self) -> bool:
        for column in self.board:
            if len(column) != self.height:
                return False
        return True
    def get_column_height(self, pos: int) -> int:
        return len(self.board[pos])
    def get_top_piece(self, pos: int) -> (str | None):
        return self.get_piece_at(pos, self.get_column_height(pos) - 1)
    def get_piece_at(self, pos: int, vert: int) -> (str | None):
        try:
            return self.board[pos][vert]
        except:
            return None
    def get_piece_string(self, pos: int, vert: int) -> str:
        result = self.get_piece_at(pos, vert)
        return result if result is not None else " "
    def to_string(self) -> str:
        result = "│" + "▕▎".join([str(x) for x in range(0, self.width)]) + "│"
        result = "├──" + "───"*(self.width-2) + "──┤\n" + result
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                line += self.get_piece_string(x, y)
                if x < self.width - 1:
                    line += "  "
            result = "│" + line + f"│ {y}\n" + result
            
        result = "┌──" + "───"*(self.width-2) + "──┐\n" + result
        result = f"To win, must get {self.win_length} in a row.\n\n" + result
        result += "\n└──" + "───"*(self.width-2) + "──┘"
        return result
                    

class BoardTreeNode:
    def __init__(self, board: Board):
        self.board: Board = board
        # Score is positive for p1 win, negative for p2 win
        self.score: float = 0
        # Index of child board node represents move at that position
        self.children: list[BoardTreeNode | int] = []
        self.up_ratio: float = 0.5
    def populate(self) -> float:
        # "solved" = all possible subsequent moves end the game
        solved = True
        # For each column you can play a piece in
        for pos in range(self.board.width):
            # Copy the current node board to edit
            child_board = self.board.copy()
            # legal is false if column is full, pr true if the move works
            legal = child_board.insert_piece(pos, self.board.turn)
            win = child_board.check_win(pos)
            full = child_board.is_full()
            # Each one is a solved case; nothing can be done after going in this position.
            if win or full or not legal:
                point = 0
                # Full boards or illegal moves are not weighted.
                if win:
                    point = 1 if self.board.turn == self.board.p1 else -1
                # Store the point with the rest of the children. Mix types, make it weird :/
                # self.children[pos] = point
                self.children.append(point)
            else:
                # Unsolved case is: not full, not a win, and a legal move.
                solved = False
                # Make sure we change turns before requesting the next node to populate.
                child_board.change_turn()
                # Add the unsolved board to a new node for later population.
                new_node = BoardTreeNode(child_board)
                # self.children[pos] = new_node
                self.children.append(new_node)
        # postcondition: self.children are either unpopulated nodes or points
        # postcondition: solved is accurate
        subscore = 0
        for child in self.children:
            if isinstance(child, BoardTreeNode):
                # Child is unsolved board, recurse solve and get score.
                # Give less points to distant solutions (L + RATIO)
                subscore += child.populate() * self.up_ratio
            else:
                # child is solved board score
                subscore += child
        self.score = subscore
        return self.score
    def get_best_pos(self, for_p1: bool = True) -> int:
        # Call after populating
        best_score = None
        best_pos = None
        for pos in range(len(self.children)):
            child = self.children[pos]
            # Get the subscore for the pos
            if isinstance(child, BoardTreeNode):
                subscore = child.score * self.up_ratio
            else:
                subscore = child
            print(f"iter chil subscr: {subscore}")
            # Default best
            if best_score is None:
                best_score = subscore
                best_pos = pos
            else:
                # "Best" depends on which player is asking
                if for_p1 and best_score < subscore:
                    best_score = subscore
                    best_pos = pos
                if not for_p1 and best_score > subscore:
                    best_score = subscore
                    best_pos = pos
        return best_pos if best_pos is not None else 0
            
            
            
def get_best_move(board: Board) -> int:
    tree = BoardTreeNode(board)
    tree.populate()
    return tree.get_best_pos()

def get_bot_response(board: Board, bot_piece: str) -> str:
    legal = [x for x in range(board.width)]
    choice = random.choice(legal)
    while board.get_column_height(choice) == board.height:
        legal.remove(choice)
        if len(legal) == 0:
            print("Bot cannot make a move!")
            break
        choice = random.choice(legal)
    return str(choice)

BOT = True

def game(win_length: int, width: int, height: int, bot_p1: bool = False):
    board = Board(win_length, width, height)
    BOT_PLAYER = board.p1 if bot_p1 else board.p2
    win = False
    change_turn = False
    tree = BoardTreeNode(board)
    if BOT:
        print("Populating bot decision tree...")
        tree.populate()
    while not win:
        change_turn = False
        print("\n" + board.to_string())
        print(f"It is '{board.turn}'s turn.")
        print("Type the number of the column to play in.")
        if BOT and board.turn == BOT_PLAYER:
            # user_input = get_bot_response(board, board.p2)
            user_input = tree.get_best_pos(False)
        else:
            user_input = input()
        try:
            pos = int(user_input)
            if board.insert_piece(pos, board.turn):
                change_turn = True
                win = board.check_win(pos)
                if win:
                    break
                if BOT:
                    if isinstance(tree, BoardTreeNode) and isinstance(tree.children[pos], BoardTreeNode):
                        tree = typing.cast(BoardTreeNode, tree.children[pos])
            else:
                print("Can't go there!")
        except Exception as e:
            print(f"Bad input! {e}")
        if change_turn:
            board.change_turn()
    print(board.to_string())
    print(f"{board.turn} won the game!")

# python main.py <connect X> <width> <height>
# Default: python main.py 4 7 6
if __name__ == "__main__":
    if len(sys.argv) not in [1, 4]:
        print("Usage: python main.py <connect X> <width> <height>")
        print("Default params: python main.py 4 7 6")
        quit()
    if len(sys.argv) == 1:
        game(4, 7, 6)
    if len(sys.argv) == 4:
        try:
            win_length = int(sys.argv[1])
            width = int(sys.argv[2])
            height = int(sys.argv[3])
            game(win_length, width, height)
        except ValueError:
            print("All arguments must be integers!")