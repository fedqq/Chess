from tkinter import *
from copy import copy
from Check import check_check, check_mate
from math import floor

SPACE_SIZE = 120
MAIN_BG = '#B48767'
SQUARE_BG = '#EBD6B7'
BASE_TIME = 1200
INCREMENT = 500

class Chess:
    def __init__(self) -> None:
        self.window = Tk()
        self.window.title('Chess')
        self.window.resizable(False, False)
        self.window.configure(bg = "black")
        self.selected = (False, (0, 0))
        self.selected_square = (0, 0)
        self.any_selected = False
        
        self.images = {'pawn':      {False : PhotoImage(file = 'resources/pawn-w.png'), 
                                     True : PhotoImage(file = 'resources/pawn-b.png')}, 
                       'lrook':      {False : PhotoImage(file = 'resources/rook-w.png'), 
                                     True : PhotoImage(file = 'resources/rook-b.png')}, 
                       'rrook':      {False : PhotoImage(file = 'resources/rook-w.png'), 
                                     True : PhotoImage(file = 'resources/rook-b.png')}, 
                       'knight':    {False : PhotoImage(file = 'resources/knight-w.png'), 
                                     True : PhotoImage(file = 'resources/knight-b.png')}, 
                       'bishop':    {False : PhotoImage(file = 'resources/bishop-w.png'), 
                                     True : PhotoImage(file = 'resources/bishop-b.png')}, 
                       'queen':     {False : PhotoImage(file = 'resources/queen-w.png'), 
                                     True : PhotoImage(file = 'resources/queen-b.png')}, 
                       'king':      {False : PhotoImage(file = 'resources/king-w.png'), 
                                     True : PhotoImage(file = 'resources/king-b.png')},
                       
                       'move-take':         PhotoImage(file = 'resources/move-take.png'), 
                       'move-circle':       PhotoImage(file = 'resources/move-circle.png'), 
                       'highlight':         PhotoImage(file = 'resources/highlight.png'), 
                       'highlight-circle':  PhotoImage(file = 'resources/highlight-circle.png'), 
                       'highlight-take':    PhotoImage(file = 'resources/highlight-take.png'), 
                       'check':             PhotoImage(file = 'resources/check.png')
                       }
        
        self.canvas = Canvas(self.window, bg = MAIN_BG, width = SPACE_SIZE * 8, height = SPACE_SIZE * 8, bd = 0, relief = RAISED)
        self.label = Label(self.window, text = 'White:     Black: ', bg = 'black', font = ('helvetica 16'), fg = 'white')
        self.label.pack()

        self.rows = [[0 for _ in range(0, 8)] for _ in range(0, 8)]
        
        i = 0
        for row in range(len(self.rows)):
            for square in range(len(self.rows[row])):
                if ((square + (row * 8)) + i) % 2 == 0:
                    x = square * SPACE_SIZE
                    y = row * SPACE_SIZE
                    self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill = SQUARE_BG, outline = '', tag = 'bg')
            i += 1
            
        self.canvas.tag_lower('bg')

        self.canvas.pack()
        
        self.game_started = False
        self.moves = []
        self.turn = 'white'
        self.playing = False
        self.king_moved_w = False
        self.king_moved_b = False
        self.rooks_moved_w = (False, False)
        self.rooks_moved_b = (False, False)
        self.en_passants_w = []
        self.en_passants_b = []
            
        self.window.bind('<Motion>', self.motion)
        self.window.bind('<Button-1>', self.click)
        self.window.bind('<Up>', self.asdf)
        
        self.start_game()
        
        self.window.mainloop()
        
    def start_game(self):
        self.canvas.delete('piece')
        self.canvas.delete('check')
        self.canvas.delete('highlight')
        self.canvas.delete('hover')
        self.timer = [BASE_TIME, BASE_TIME]
        self.playing = True
        self.timer_started = False
        self.turn = 'white'
        self.moves = []
        
        self.rows = [
                     [Piece((1, 1), self, True, 'lrook'), Piece((2, 1), self, True, 'knight'), Piece((3, 1), self, True, 'bishop'), Piece((4, 1), self, True, 'queen'), Piece((5, 1), self, True, 'king'), Piece((6, 1), self, True, 'bishop'), Piece((7, 1), self, True, 'knight'), Piece((8, 1), self, True, 'rrook')], 
                     [Piece((number + 1, 2), self, True) for number in range(8)], 
                     [0 for _ in range(0, 8)],
                     [0 for _ in range(0, 8)], 
                     [0 for _ in range(0, 8)], 
                     [0 for _ in range(0, 8)], 
                     [Piece((number + 1, 7), self, False) for number in range(8)],
                     [Piece((1, 8), self, False, 'lrook'), Piece((2, 8), self, False, 'knight'), Piece((3, 8), self, False, 'bishop'), Piece((4, 8), self, False, 'queen'), Piece((5, 8), self, False, 'king'), Piece((6, 8), self, False, 'bishop'), Piece((7, 8), self, False, 'knight'), Piece((8, 8), self, False, 'rrook')], 
                    ]
        
        self.black_king = (4, 0)
        self.white_king = (4, 7)
        
    def asdf(self, e):
        self.start_game()
        
    def motion(self, event):
            self.canvas.delete('hover')
            x = event.x - event.x % SPACE_SIZE
            y = event.y - event.y % SPACE_SIZE
            
            self.x = int(x / SPACE_SIZE)
            if self.x > 7:
                self.x = 7
            elif self.x < 0:
                self.x = 0
            self.y = int(y / SPACE_SIZE)
            if self.y > 7:
                self.y = 7
            elif self.y < 0:
                self.y = 0
                
            
            
            if len(self.moves) != 0:
                full_passant = self.en_passants_b + self.en_passants_w
                if (self.x, self.y) in self.moves or len([a for a in full_passant if a[:2] == (self.x, self.y)]) == 1:
                    if type(self.rows[self.y][self.x]) is Piece:
                        self.canvas.create_image(x, y, image = self.images['highlight-take'], anchor = NW, tag = 'hover')
                    else:
                        self.canvas.create_image(x, y, image = self.images['highlight-circle'], anchor = NW, tag = 'hover')
                    self.canvas.tag_raise('piece')
        
    def switch_turn(self):
        
        if self.turn == 'white':
            self.turn = 'black'
            self.timer[1] += INCREMENT
            self.en_passants_b.clear()
        else:
            self.turn = 'white'
            self.timer[0] += INCREMENT
            self.en_passants_w.clear()
        
    def click(self, event):
        
        self.canvas.delete('moves', 'check', 'hover')
        
        if not self.timer_started:
            self.timer_started = True
            self.tick_timer()
            
        click_square: Piece = self.rows[self.y][self.x]
        click_position = (self.x, self.y)
        
        if self.any_selected:
            selected_square: Piece = self.rows[self.selected_square[1]][self.selected_square[0]]
            current_moves = selected_square.get_moves(self.selected_square)
            shortened_moves = [a[:1] for a in current_moves]
            
            if len([a for a in current_moves if a[0] == click_position[0] and a[1] == click_position[1]]) == 1:
                
                square_sprite = selected_square.sprite
                
                if type(click_square) is Piece:
                    self.canvas.delete(click_square.sprite)
                    
                if selected_square.type == 'king':
                    if selected_square.black:
                        self.king_moved_b = True
                        self.black_king = click_position
                    else:
                        self.king_moved_w = True
                        self.white_king = click_position
                    
                    if selected_square.black:
                        row = 0
                    else:
                        row = 7
                        
                    if click_position[0] - self.selected_square[0] == 2:
                        self.canvas.move(self.rows[row][-1].obj, SPACE_SIZE * -2, 0)
                        self.rows[row][5] = copy(self.rows[row][-1])
                        self.rows[row][-1] = 0
                    elif click_position[0] - self.selected_square[0] == -2:
                        self.canvas.move(self.rows[row][0].obj, SPACE_SIZE * 3, 0)
                        self.rows[row][3] = copy(self.rows[row][0])
                        self.rows[row][0] = 0
                        
                if 'rook' in selected_square.type:
                    if selected_square.black:
                        if selected_square.type == 'lrook':
                            self.rooks_moved_b = (True, self.rooks_moved_b[1])
                        else:
                            self.rooks_moved_b = (self.rooks_moved_b[0], True)
                    else:
                        if selected_square.type == 'lrook':
                            self.rooks_moved_w = (True, self.rooks_moved_w[1])
                        else:
                            self.rooks_moved_w = (self.rooks_moved_w[0], True)
                            
                if selected_square.type == 'pawn':
                    
                    if abs(self.selected_square[1] - click_position[1]) == 2:
                        object = (self.selected_square[0], int((self.selected_square[1] + click_position[1]) / 2), click_position[0], click_position[1])
                        if selected_square.black:
                            self.en_passants_b.append(object)
                        else:
                            self.en_passants_w.append(object)
                            
                move = [a for a in current_moves if a[0] == click_position[0] and a[1] == click_position[1]][0]
                if len(move) > 2:
                    print(move)
                    print([move[3], move[2]])
                    self.canvas.delete(self.rows[move[3]][move[2]].sprite)
                    self.rows[move[3]][move[2]] = 0
                
                self.rows[click_position[1]][click_position[0]] = copy(selected_square)
                self.rows[self.selected_square[1]][self.selected_square[0]] = 0
                self.switch_turn()
                
                self.canvas.moveto(square_sprite, y = self.y * SPACE_SIZE, x = self.x * SPACE_SIZE)
                
                self.canvas.delete('highlight')
                self.moves = []
                self.any_selected = False
                self.selected_square = ()
            else:
                if click_square == selected_square:
                    self.canvas.delete('moves')
                    self.canvas.delete('highlight')
                    self.moves = []
                    self.any_selected = False
                    self.selected_square = ()
                    self.check_check()
                    return
                self.canvas.delete('moves')
                self.moves = []
                self.any_selected = False
                self.selected_square = ()
                self.canvas.delete('highlight')
                black = (self.turn == 'black')
                if type(click_square) is Piece:
                    if click_square.black == black or (1 == 1):
                        self.any_selected = True
                        click_square.select(click_position)
                        self.draw_moves(click_square.get_moves(click_position))
                        self.selected_square = click_position
                    else:
                        self.moves = []
                        self.any_selected = False
                
        else:
            if type(click_square) is not int:
                black = (self.turn == 'black')
                if click_square.black == black or (1 == 1):
                    click_square.select(click_position)
                    self.selected_square = click_position
                    self.any_selected = True
                    self.draw_moves(click_square.get_moves(click_position))
        
        self.check_check()
        
    def tick_timer(self):
        if self.turn == 'white':
            self.timer[0] -= 1
        else:
            self.timer[1] -= 1
        
        white = f'{floor(self.timer[0]/60)}:{self.timer[0] % 60}'
        black = f'{floor(self.timer[1]/60)}:{self.timer[1] % 60}'
        self.label.configure(text = f'White: {white}    Black: {black}')
        
        self.window.after(1000, self.tick_timer)
        
                        
    def check_check(self, rows = '') -> tuple:
        self.canvas.delete('check')
        if rows == '':
            rows = self.rows
        
        check = check_check(rows, self.white_king, self.black_king) 
        
        if check:
            mate = check_mate(rows, self.white_king, 'w')
        else:
            mate = False
            
        if check == 'white':
            king = self.white_king
        else:
            king = self.black_king
            
        self.canvas.create_image(proportion(king), image = self.images['check'], tag = 'check', anchor = NW)
        
        return (check, False)
            
    def draw_moves(self, moves):
        self.moves = moves
        for move in moves:
            string = 'move-circle'
            if type(self.rows[move[1]][move[0]]) is Piece:
                string = 'move-take'
            self.canvas.create_image(proportion(move), image = self.images[string], anchor = NW, tag = 'moves')
            self.canvas.tag_raise('piece')
            
class Testpiece:
    def __init__(self, base):
        if type(base) is not int:
            
            self.type = base.type
            self.black = base.black
            self.coordinates = (base.coordinates[0] - 1, base.coordinates[1] - 1)
            self.selected = False
            
    def __str__(self) -> str:
        return f'{self.type}'
    def __unicode__(self):
        return f'{self.type}'
    def __repr__(self):
        return f'{self.type}'
    
class Piece:
    def __init__(self, coordinates = '', game: Chess = None, black = False, piece_type = 'pawn') -> None:
        self.type = piece_type
        self.game = game
        self.black = black
        self.has_enpassant = False
        
        self.coordinates = (coordinates[0] - 1, coordinates[1] - 1)
        
        self.sprite = self.game.canvas.create_image(proportion(self.coordinates), image = self.game.images[self.type][self.black], anchor = NW, tag = 'piece')
            
    def select(self, position):
        self.game.canvas.create_image(proportion(position), image = self.game.images['highlight'], anchor = NW, tag = 'highlight')
        self.game.canvas.tag_raise('piece')
        
    def get_moves(self, coordinates):
        moves = []
        multiplier = -1
        if self.black:
            multiplier = 1
            
        current_x = coordinates[0]
        current_y = coordinates[1]
        
        def check_moves(x_inc, y_inc):
            x = copy(current_x) + x_inc
            y = copy(current_y) + y_inc
                        
            while self.get(y, x) != 'NA':
                            
                piece: Piece = self.get(y, x)
                if type(piece) is Piece:
                    if piece.black != self.black:
                        moves.append((x, y))
                    break
                            
                moves.append((x, y))
                x += x_inc
                y += y_inc
        
        match self.type:
            
            case 'king':
                
                def check(x, y):
                    square = self.get(y, x)
                    if type(square) is not str:
                        if type(square) is int or square.black != self.black:
                            moves.append((x, y))
                
                check(current_x, current_y + 1)
                check(current_x + 1, current_y)
                check(current_x - 1, current_y)
                check(current_x, current_y - 1)
                check(current_x + 1, current_y + 1)
                check(current_x + 1, current_y - 1)
                check(current_x - 1, current_y + 1)
                check(current_x - 1, current_y - 1)
                
                if not self.game.king_moved_w:
                    if not self.game.rooks_moved_w[0]:
                        if self.game.rows[7][1] == 0 and self.game.rows[7][2] == 0 and self.game.rows[7][3] == 0:
                            moves.append((current_x - 2, current_y))
                    if not self.game.rooks_moved_w[0]:
                        if self.game.rows[7][5] == 0 and self.game.rows[7][6] == 0:
                            moves.append((current_x + 2, current_y))
                            
                if not self.game.king_moved_b:
                    if not self.game.rooks_moved_b[0]:
                        if self.game.rows[0][1] == 0 and self.game.rows[0][2] == 0 and self.game.rows[0][3] == 0:
                            moves.append((current_x - 2, current_y))
                    if not self.game.rooks_moved_b[0]:
                        if self.game.rows[0][5] == 0 and self.game.rows[0][6] == 0:
                            moves.append((current_x + 2, current_y))
            
            case 'pawn':
                if self.coordinates == coordinates:
                    if self.get(current_y + 1 * multiplier, current_x) == 0:
                        moves.append((current_x, current_y + 1 * multiplier))
                        if self.get(current_y + 2 * multiplier, current_x) == 0:
                            moves.append((current_x, current_y + 2 * multiplier))
                else:
                    if self.get(current_y + 1 * multiplier, current_x) == 0:
                        moves.append((current_x, current_y + 1 * multiplier))
                
                if type(self.get(current_y + 1 * multiplier, current_x + 1 * multiplier)) is Piece:
                    if self.game.rows[current_y + 1 * multiplier][current_x + 1 * multiplier].black != self.black:
                        moves.append((current_x + 1 * multiplier, current_y + 1 * multiplier))
                
                if type(self.get(current_y + 1 * multiplier, current_x - 1 * multiplier)) is Piece:
                    if self.game.rows[current_y + 1 * multiplier][current_x - 1 * multiplier].black != self.black:
                        moves.append((current_x - 1 * multiplier, current_y + 1 * multiplier))
                
                if self.black:
                    en_passants = self.game.en_passants_w
                else:
                    en_passants = self.game.en_passants_b
                
                found_passant = [a for a in en_passants if a[0] == current_x - 1 * multiplier and a[1] == current_y + 1 * multiplier]
                if len(found_passant) == 1:
                    moves.append((current_x - 1 * multiplier, current_y + 1 * multiplier, found_passant[0][2], found_passant[0][2]))
                found_passant = [a for a in en_passants if a[0] == current_x + 1 * multiplier and a[1] == current_y + 1 * multiplier]
                if len(found_passant) == 1:
                    moves.append((current_x + 1 * multiplier, current_y + 1 * multiplier, found_passant[0][2], found_passant[0][3]))
                      
            case 'knight':
                
                for move in ((2, 1), (1, 2), (-2, 1), (2, -1), (-2, -1), (-1, 2), (-1, -2), (1, -2)):
                    piece = self.get(current_y + move[0], current_x + move[1])
                    if piece != 'NA':
                        if type(piece) is Piece:
                            if piece.black != self.black:
                                moves.append((current_x + move[1], current_y + move[0]))
                        else:
                            moves.append((current_x + move[1], current_y + move[0]))
                            
            case _:
                if self.type == 'rrook' or self.type == 'queen' or self.type == 'lrook':
                            
                    check_moves(1, 0)
                    check_moves(-1, 0)
                    check_moves(0, 1)
                    check_moves(0, -1)
                
                if self.type == 'bishop' or self.type == 'queen':
                    
                    check_moves(1, 1)
                    check_moves(1, -1)
                    check_moves(-1, 1)
                    check_moves(-1, -1)
        
        legal_moves = []
        for move in moves:
            
            test_rows = []
            for row in self.game.rows:
                test_rows.append([])
                for square in row:
                    if type(square) is int:
                        test_rows[-1].append(0)
                    else:
                        test_rows[-1].append(Testpiece(square))
            
            test_rows[move[1]][move[0]] = copy(test_rows[current_y][current_x])
            test_rows[current_y][current_x] = 0
            if self.black:
                string = 'black'
            else:
                string = 'white'
            
            if self.type == 'king':
                white_king, black_king = (0, 0), (0, 0)
                
                for row_number in range(len(test_rows)):
                    for square_number in range(len(test_rows[row_number])):
                        square = test_rows[row_number][square_number]
                        if square == 0:
                            continue
                        else:
                            if square.type == 'king':
                                if square.black:
                                    black_king = (square_number, row_number)
                                else:
                                    white_king = (square_number, row_number)
                                    
                test = check_check(test_rows, white_king, black_king)
                
            else:
                test = check_check(test_rows, self.game.white_king, self.game.black_king)
                
            if test != string:
                legal_moves.append(move)
            
        return legal_moves
    
    def get(self, y, x):
        if y not in range(0, 8) or x not in range(0, 8):
            return 'NA'
        else:
            return self.game.rows[y][x]
        
    def __str__(self) -> str:
        return f'{self.type}'
    def __unicode__(self):
        return f'{self.type}'
    def __repr__(self):
        return f'{self.type}'
    
def proportion(tuple):
    return [a * SPACE_SIZE for a in tuple]
    
Chess()