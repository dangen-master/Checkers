WHITE = 1
BLACK = 2
LOSE = False
ROOKS = [[False, False], [False, False]]
KINGS = [False, False]


def opponent(color):
    if color == WHITE:
        return BLACK
    else:
        return WHITE


def print_board(board):
    print('     +----+----+----+----+----+----+----+----+')
    for row in range(7, -1, -1):
        print(' ', row, end='  ')
        for col in range(8):
            print('|', board.cell(row, col), end=' ')
        print('|')
        print('     +----+----+----+----+----+----+----+----+')
    print(end='        ')
    for col in range(8):
        print(col, end='    ')
    print()


def main():
    global LOSE
    board = Board()
    while not LOSE:
        print_board(board)
        print('Команды:')
        print('    exit                               -- выход')
        print('    move <row> <col> <row1> <row1>     -- ход из клетки (row, col)')
        print('                                          в клетку (row1, col1)')
        print('    castling0                          -- рокировка в ладьей')
        print('                                          из колонки 0')
        print('    castling7                          -- рокировка в ладьей')
        print('                                          из колонки 7')
        if board.current_player_color() == WHITE:
            print('Ход белых:')
        else:
            print('Ход чёрных:')
        command = input()
        res = False
        if command == 'exit':
            break
        elif command == 'castling7':
            res = board.castling7()
        elif command == 'castling0':
            res = board.castling0()
        elif command.split()[0] == 'move':
            row, col, row1, col1 = [int(i) for i in command.split()[1:]]
            res = board.move_piece(row, col, row1, col1)
        for i in range(len(board.field)):
            for k in range(len(board.field[i])):
                if isinstance(board.field[i][k], King) and (board.field[i][k].color == board.color):
                    king, c1, c2 = board.field[i][k], i, k
        LOSE = True
        for i in range(len(board.field)):
            for k in range(len(board.field[i])):
                if king.can_move(board, c1, c2, i, k):
                    print(i, k)
                    LOSE = False
                    break
        if LOSE:
            break
        if res:
            print('Ход успешен')
        else:
            print('Ошибка!')
    print_board(board)
    print('Победил белый' if board.color == BLACK else 'Победил черный')


def correct_coords(row, col):
    return 0 <= row < 8 and 0 <= col < 8


class Board:

    def __init__(self):
        self.color = WHITE
        self.field = []
        for row in range(8):
            self.field.append([None] * 8)
        self.field[0] = [
            Rook(WHITE), Knight(WHITE), Bishop(WHITE), Queen(WHITE),
            King(WHITE), Bishop(WHITE), Knight(WHITE), Rook(WHITE)
        ]
        self.field[1] = [
            Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE),
            Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE)
        ]
        self.field[6] = [
            Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK),
            Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK)
        ]
        self.field[7] = [
            Rook(BLACK), Knight(BLACK), Bishop(BLACK), Queen(BLACK),
            King(BLACK), Bishop(BLACK), Knight(BLACK), Rook(BLACK)
        ]

    def current_player_color(self):
        return self.color

    def cell(self, row, col):
        piece = self.field[row][col]
        if piece is None:
            return '  '
        color = piece.get_color()
        c = 'w' if color == WHITE else 'b'
        return c + piece.char()

    def get_piece(self, row, col):
        if correct_coords(row, col):
            return self.field[row][col]
        else:
            return None

    def move_piece(self, row, col, row1, col1):
        global LOSE
        if not correct_coords(row, col) or not correct_coords(row1, col1):
            return False
        if row == row1 and col == col1:
            return False
        piece = self.field[row][col]
        target = self.field[row1][col1]
        if piece is None:
            return False
        if self.field[row1][col1] is None:
            if not piece.can_move(self, row, col, row1, col1):
                return False
        elif self.field[row1][col1].get_color() == opponent(piece.get_color()):
            if not piece.can_attack(self, row, col, row1, col1):
                return False
        else:
            return False
        a = isinstance(self.field[row][col], Pawn)
        a = a and ((self.field[row][col].color == WHITE) and (row1 == 7))
        b = isinstance(self.field[row][col], Pawn)
        b = b and ((self.field[row][col].color == BLACK) and (row1 == 0))
        if a or b:
            print('Выберите фигуру для превращения')
            print('N - конь')
            print('Q - ферзь')
            print('R - ладья')
            print('B - слон')
            command = ''
            while command not in ['N', 'Q', 'R', 'B']:
                print('Неверно, попробуй ещё раз')
                command = input()
            self.move_and_promote_pawn(row, col, row1, col1, command)
        else:
            self.field[row][col] = None
            self.field[row1][col1] = piece
            self.color = opponent(self.color)
        for i in range(len(self.field)):
            for k in range(len(self.field[i])):
                a = (self.field[i][k].color == opponent(self.color))
                if isinstance(self.field[i][k], King) and a:
                    if self.is_under_attack(i, k, self.color):
                        near = [[1, 1], [1, 0], [1, -1], [0, 1], [0, -1], [-1, 1], [-1, 0], [-1, -1]]
                        LOSE = True
                        for j in range(len(near)):
                            if self.field[i][k].can_move(self, i, k, i + near[j][0], k + near[j][1]):
                                LOSE = False
                                break
                        self.field[row][col] = piece
                        self.field[row1][col1] = target
                        self.color = opponent(self.color)
                        return False
        return True

    def is_under_attack(self, row, col, color):
        for i in range(len(self.field)):
            for k in range(len(self.field[i])):
                if self.field[i][k]:
                    if self.field[i][k].get_color() == color:
                        if self.field[i][k].can_attack(self, i, k, row, col, True):
                            return True
        return False

    def move_and_promote_pawn(self, row, col, row1, col1, char):
        if char == 'N':
            self.field[row1][col1] = Knight(self.field[row][col].get_color())
        elif char == 'R':
            self.field[row1][col1] = Rook(self.field[row][col].get_color())
        elif char == 'Q':
            self.field[row1][col1] = Queen(self.field[row][col].get_color())
        elif char == 'B':
            self.field[row1][col1] = Bishop(self.field[row][col].get_color())
        self.field[row][col] = None

    def castling0(self):
        r = 0 if self.color == WHITE else 7
        for i in range(1, 4):
            if not (self.field[r][i] is None):
                return False
        if isinstance(self.field[r][4], King) and (self.field[r][4].color == self.color):
            if isinstance(self.field[r][0], Rook) and (self.field[r][0].color == self.color):
                if not (KINGS[self.color - 1]) and not (ROOKS[self.color - 1][0]):
                    self.field[r][0] = None
                    self.field[r][4] = None
                    self.field[r][2] = King(self.color)
                    self.field[r][3] = Rook(self.color)
                    self.color = opponent(self.color)
                    return True
        return False

    def castling7(self):
        r = 0 if self.color == WHITE else 7
        for i in range(5, 7):
            if not (self.field[r][i] is None):
                return False
        if isinstance(self.field[r][4], King) and (self.field[r][4].color == self.color):
            if isinstance(self.field[r][7], Rook) and (self.field[r][7].color == self.color):
                if not (KINGS[self.color - 1]) and not (ROOKS[self.color - 1][1]):
                    self.field[r][7] = None
                    self.field[r][4] = None
                    self.field[r][6] = King(self.color)
                    self.field[r][5] = Rook(self.color)
                    self.color = opponent(self.color)
                    return True
        return False


class Figure:

    def __init__(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def can_attack(self, board, row, col, row1, col1, ignore=False):
        return self.can_move(board, row, col, row1, col1, ignore)


class Rook(Figure):

    def char(self):
        return 'R'

    def can_move(self, board, row, col, row1, col1, ignore=False):
        if row == row1 and col == col1:
            return False
        if (row1 >= 0) and (col1 >= 0) and (row1 < 8) and (col1 < 8):
            if (row != row1) and (col != col1):
                return False
            if ignore and (row == row1 or col == col1):
                return True
            step = 1 if (row1 >= row) else -1
            for r in range(row + step, row1, step):
                if not (board.get_piece(r, col) is None):
                    if ignore and (r == row1):
                        if col == 0:
                            ROOKS[self.color - 1][0] = True
                        elif col == 7:
                            ROOKS[self.color - 1][1] = True
                        return True
                    if board.field[r][col].get_color() != self.color:
                        if r == row1:
                            if col == 0:
                                ROOKS[self.color - 1][0] = True
                            elif col == 7:
                                ROOKS[self.color - 1][1] = True
                            return True
                    return False

            step = 1 if (col1 >= col) else -1
            for c in range(col + step, col1, step):
                if not (board.get_piece(row, c) is None):
                    if ignore and (c == col1):
                        if col == 0:
                            ROOKS[self.color - 1][0] = True
                        elif col == 7:
                            ROOKS[self.color - 1][1] = True
                        return True
                    if board.field[row][c].get_color() != self.color:
                        if c == col1:
                            if col == 0:
                                ROOKS[self.color - 1][0] = True
                            elif col == 7:
                                ROOKS[self.color - 1][1] = True
                            return True
                    return False
            if col == 0:
                ROOKS[self.color - 1][0] = True
            elif col == 7:
                ROOKS[self.color - 1][1] = True
            return True
        return False


class Pawn(Figure):

    def char(self):
        return 'P'

    def can_move(self, board, row, col, row1, col1, ignore=False):
        if row == row1 and col == col1:
            return False
        if col != col1:
            return False
        if self.color == WHITE:
            direction = 1
            start_row = 1
        else:
            direction = -1
            start_row = 6
        if row + direction == row1:
            return True
        if (row == start_row
                and row + 2 * direction == row1
                and board.field[row + direction][col] is None):
            return True

        return False

    def can_attack(self, board, row, col, row1, col1, ignore=False):
        direction = 1 if (self.color == WHITE) else -1
        return (row + direction == row1
                and (col + 1 == col1 or col - 1 == col1))


class Knight(Figure):

    def char(self):
        return 'N'

    def can_move(self, board, row, col, row1, col1, ignore=False):
        if row == row1 and col == col1:
            return False
        near = [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]]

        for i in range(len(near)):
            x = row + near[i][0]
            y = col + near[i][1]

            if (x >= 0) and (y >= 0) and (x < 8) and (y < 8):
                if (x == row1) and (y == col1):
                    return True
        return False


class King(Figure):

    def char(self):
        return 'K'

    def can_move(self, board, row, col, row1, col1, ignore=False):
        if row == row1 and col == col1:
            return False
        near = [[1, 1], [1, 0], [1, -1], [0, 1], [0, -1], [-1, 1], [-1, 0], [-1, -1]]
        for i in range(len(near)):
            x = row + near[i][0]
            y = col + near[i][1]

            if (x >= 0) and (y >= 0) and (x < 8) and (y < 8):
                if (x == row1) and (y == col1):
                    if not ignore:
                        if not (board.field[x][y] is None):
                            if (board.field[x][y].get_color() != self.color):
                                if not board.is_under_attack(x, y, opponent(self.color)):
                                    KINGS[self.color - 1] = True
                                    return True
                        else:
                            if not board.is_under_attack(x, y, opponent(self.color)):
                                KINGS[self.color - 1] = True
                                return True
                            else:
                                return False
                    else:
                        KINGS[self.color - 1] = True
                        return True
                    return False
        return False


class Queen(Figure):

    def char(self):
        return 'Q'

    def can_move(self, board, row, col, row1, col1, ignore=False):
        if row == row1 and col == col1:
            return False
        if (row1 >= 0) and (col1 >= 0) and (row1 < 8) and (col1 < 8):
            if (abs(row1 - row) == abs(col1 - col)):

                stepx = 1 if row < row1 else -1
                stepy = 1 if col < col1 else -1

                for c in range(1, abs(row1 - row)):
                    if not (board.field[row + stepx * c][col + stepy * c] is None):
                        return False

                if not (board.get_piece(row1, col1) is None):
                    if not ignore:
                        if board.field[row1][col1].get_color() == self.color:
                            return False
                        else:
                            return True
                    else:
                        return True
                return True

            if (row != row1) and (col != col1):
                return False
            if col1 == col:
                step = 1 if (row1 > row) else -1
                for r in range(row + step, row1, step):
                    if not (board.get_piece(r, col) is None):
                        return False

            elif row1 == row:
                step = 1 if (col1 > col) else -1
                for c in range(col + step, col1, step):
                    if not (board.get_piece(row, c) is None):
                        return False

            if not (board.get_piece(row1, col1) is None):
                if not ignore:
                    if board.field[row1][col1].get_color() == self.color:
                        return False
                    else:
                        return True
                else:
                    return True
            return True


class Bishop(Figure):

    def char(self):
        return 'B'

    def can_move(self, board, row, col, row1, col1, ignore=False):
        if row == row1 and col == col1:
            return False
        if (row1 >= 0) and (col1 >= 0) and (row1 < 8) and (col1 < 8):
            if (abs(row1 - row) != abs(col1 - col)):
                return False
            stepx = 1 if row < row1 else -1
            stepy = 1 if col < col1 else -1
            for c in range(1, row1 - row):
                if not (board.field[row + stepx * c][col + stepy * c] is None):
                    if not ignore:
                        if board.field[row + stepx * c][col + stepy * c].get_color() == self.color:
                            return False
                        return True
                    else:
                        return True
            return True
        return False


if __name__ == "__main__":
    main()