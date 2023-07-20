"""Connect 4 implementation in python, command line."""
import random

class Board:
    def __init__(self, width: int = 7, height: int = 6):
        self.board: list[list[str]] = [[] for _ in range(width)]
        self.width = width
        self.height = height
        self.win_length = 4
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
        result = "│" + "  ".join([str(x) for x in range(0, self.width)]) + "│"
        result = "├──" + "───"*(self.width-2) + "──┤\n" + result
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                line += self.get_piece_string(x, y)
                if x < self.width - 1:
                    line += "  "
            result = "│" + line + "│\n" + result
        result = "┌──" + "───"*(self.width-2) + "──┐\n" + result
        return result
    
BOT = True

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
        
    

def game():
    board = Board()
    p1 = "o"
    p2 = "x"
    win = False
    change_turn = False
    turn = p1
    while not win:
        change_turn = False
        print(board.to_string())
        print(f"It is '{turn}'s turn.")
        print("Type the number of the column to play in.")
        if BOT and turn == p2:
            user_input = get_bot_response(board, p2)
        else:
            user_input = input()
        try:
            pos = int(user_input)
            if board.insert_piece(pos, turn):
                change_turn = True
                win = board.check_win(pos)
                if win:
                    break
            else:
                print("Can't go there!")
        except Exception as e:
            print(f"Bad input! {e}")
        if change_turn:
            turn = p2 if turn == p1 else p1
    print(board.to_string())
    print(f"{turn} won the game!")

game()