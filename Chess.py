from tkinter import *
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
        self.window.configure(bg = MAIN_BG)
        self.selected_position = (0, 0)
        self.any_selected = False
        
        self.images = {'pawn':      {False: PhotoImage(file = 'resources/pawn-w.png'), 
                                     True : PhotoImage(file = 'resources/pawn-b.png')}, 
                       'lrook':     {False: PhotoImage(file = 'resources/rook-w.png'), 
                                     True : PhotoImage(file = 'resources/rook-b.png')}, 
                       'rrook':     {False: PhotoImage(file = 'resources/rook-w.png'), 
                                     True : PhotoImage(file = 'resources/rook-b.png')}, 
                       'knight':    {False: PhotoImage(file = 'resources/knight-w.png'), 
                                     True : PhotoImage(file = 'resources/knight-b.png')}, 
                       'bishop':    {False: PhotoImage(file = 'resources/bishop-w.png'), 
                                     True : PhotoImage(file = 'resources/bishop-b.png')}, 
                       'queen':     {False: PhotoImage(file = 'resources/queen-w.png'), 
                                     True : PhotoImage(file = 'resources/queen-b.png')}, 
                       'king':      {False: PhotoImage(file = 'resources/king-w.png'), 
                                     True : PhotoImage(file = 'resources/king-b.png')},
                       
                       'move-take':         PhotoImage(file = 'resources/move-take.png'), 
                       'move-circle':       PhotoImage(file = 'resources/move-circle.png'), 
                       'highlight':         PhotoImage(file = 'resources/highlight.png'), 
                       'highlight-circle':  PhotoImage(file = 'resources/highlight-circle.png'), 
                       'highlight-take':    PhotoImage(file = 'resources/highlight-take.png'), 
                       'check':             PhotoImage(file = 'resources/check.png')
                       }
        
        self.canvas = Canvas(self.window, bg = MAIN_BG, width = SPACE_SIZE * 8, height = SPACE_SIZE * 8, bd = 0, relief = RAISED, highlightcolor = 'black', highlightthickness = 1)
        self.label = Label(self.window, text = 'White: \tBlack: ', bg = MAIN_BG, font = ('times new roman', 27), fg = 'white', width = 20)
        self.canvas.pack(side = BOTTOM)
        self.label.pack(side = RIGHT)
        
        self.canvas.tag_lower('bg')
        
        self.turn               = 'white'
        self.playing            = False
        self.out                = False
        self.game_started       = False
        self.w_moved            = [False, False, False]
        self.b_moved            = [False, False, False]
        self.en_passants_w      = []
        self.en_passants_b      = []
        self.moves              = []
            
        self.window.bind('<Motion>',    self.motion)
        self.window.bind('<Button-1>',  self.click)
        self.window.bind('<Up>',        self.restart)
            
        def change(b):
            self.out = b
            
        self.canvas.bind('<Enter>', lambda *args: change(False))
        self.canvas.bind('<Leave>', lambda *args: change(True))
        
        self.string_checks = [[StringVar(), '1200'], [StringVar(), '500']]
        font = ('times new roman', 20)
        
        self.time_label = Label(self.window, text = 'Time: ', font = font, bg = MAIN_BG, fg = 'white')
        self.time_input = Entry(self.window, bg = MAIN_BG, fg = 'white', bd = 0, font = font, textvariable = self.string_checks[0][0], width = 7)
        self.time_input.insert(0, f'{BASE_TIME}')
        
        self.increment_label = Label(self.window, text = ' + ', font = font, bg = MAIN_BG, fg = 'white')
        self.increment_input = Entry(self.window, bg = MAIN_BG, fg = 'white', bd = 0, font = font, textvariable = self.string_checks[1][0], width = 7)
        self.increment_input.insert(0, f'{INCREMENT}')
        
        self.rows = [[0 for _ in range(0, 8)] for _ in range(0, 8)]
        
        i = 0
        for row in range(len(self.rows)):
            for square in range(len(self.rows[row])):
                if ((square + (row * 8)) + i) % 2 == 0:
                    x = square * SPACE_SIZE
                    y = row * SPACE_SIZE
                    self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill = SQUARE_BG, outline = '', tag = 'bg')
            i += 1

        self.string_checks[0][0].trace('w', lambda *args: self.check_text(True))
        self.string_checks[1][0].trace('w', lambda *args: self.check_text(False))
        
        self.canvas.create_text(500, 400, text = 'Chess\nPress anywhere to play', font = ('times new roman', 55), justify = CENTER, tag = 'title')

        self.time_label.pack(side = LEFT)
        self.time_input.pack(side = LEFT)
        self.increment_label.pack(side = LEFT)
        self.increment_input.pack(side = LEFT)
        self.window.mainloop()
        
    def check_text(self, one):
        if one:
            test = self.string_checks[0]
        else:
            test = self.string_checks[1]
        
        if (test[0].get().isdigit() or test[0].get() == '') and not self.playing and not len(test[0].get()) > 6:
            test[1] = test[0].get()
        else:
            test[0].set(test[1])
        
    def start_game(self):
        
        self.canvas.delete('title')
        
        if self.string_checks[0][1].strip() == '' or self.string_checks[1][1].strip() == '':
            return
        else:
            self.base = int(self.string_checks[0][1])
            self.increment = int(self.string_checks[1][1])
        
        self.canvas.delete('piece', 'check', 'highlight', 'hover')
        self.timer                  = [self.base, self.base]
        self.black_king             = (4, 0)
        self.white_king             = (4, 7)
        self.playing                = True
        self.timer_started          = False
        self.turn                   = 'white'
        self.moves                  = []
        
        pieces = ['lrook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rrook']
        self.rows = [
                     [Piece((number + 1, 1), self, True, pieces[number]) for number in range(8)], 
                     [Piece((number + 1, 2), self, True) for number in range(8)], 
                     [0 for _ in range(0, 8)],
                     [0 for _ in range(0, 8)], 
                     [0 for _ in range(0, 8)], 
                     [0 for _ in range(0, 8)], 
                     [Piece((number + 1, 7), self, False) for number in range(8)],
                     [Piece((number + 1, 8), self, False, pieces[number]) for number in range(8)]
                    ]
        
    def restart(self, *args):
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
                
                if element_in_list((self.x, self.y), self.moves):
                    if type(self.get(self.y, self.x)) is Piece:
                        self.canvas.create_image(x, y, image = self.images['highlight-take'], anchor = NW, tag = 'hover')
                    else:
                        self.canvas.create_image(x, y, image = self.images['highlight-circle'], anchor = NW, tag = 'hover')
                    self.canvas.tag_raise('piece')
              
    def switch_turn(self):
        
        if self.turn == 'white':
            self.turn = 'black'
            self.timer[1] += INCREMENT
        else:
            self.turn = 'white'
            self.timer[0] += INCREMENT
        
    def click(self, event):
        if not self.playing:
            if not self.out:
                self.start_game()
            return        
        
        self.canvas.delete('moves', 'check', 'hover', 'highlight')
        
        if not self.timer_started:
            self.timer_started = True
            self.tick_timer()
            
        click_position = (self.x, self.y)
        click_square: Piece = self.get(tuple = click_position)
        
        if self.any_selected:
            selected_square: Piece = self.get(tuple = self.selected_position)
            
            if element_in_list(click_position, self.moves):
                
                square_sprite = selected_square.sprite
                
                if type(click_square) is Piece:
                    self.canvas.delete(click_square.sprite)
                
                match selected_square.type:
                    case 'king':
                        if selected_square.black:
                            self.b_moved[0] = True
                            self.black_king = click_position
                        else:
                            self.w_moved[0] = True
                            self.white_king = click_position
                        
                        if selected_square.black:
                            row = 0
                        else:
                            row = 7
                            
                        if click_position[0] - self.selected_position[0] == 2:
                            
                            self.canvas.move(self.get(row, -1).sprite, SPACE_SIZE * -2, 0)
                            self.assign((5, row), self.get(row, -1))
                            self.assign((-1, row))
                            
                        elif click_position[0] - self.selected_position[0] == -2:
                            
                            self.canvas.move(self.get(row, 0).sprite, SPACE_SIZE * 3, 0)
                            self.assign((3, row), self.get(row, 0))
                            self.assign((0, row))
                                
                    case 'pawn':
                        
                        if abs(self.selected_position[1] - click_position[1]) == 2:
                            object = (self.selected_position[0], int((self.selected_position[1] + click_position[1]) / 2), click_position[0], click_position[1])
                            if selected_square.black:
                                self.en_passants_b.append(object)
                            else:
                                self.en_passants_w.append(object)
                                
                    case _:
                        if 'rook' in selected_square.type:
                            if selected_square.black:
                                if selected_square.type == 'lrook':
                                    self.b_moved[1] = True
                                else:
                                    self.b_moved[2] = True
                            else:
                                if selected_square.type == 'lrook':
                                    self.w_moved[1] = True
                                else:
                                    self.w_moved[2] = True
                            
                move = element_in_list(click_position, self.moves, True)
                if len(move) > 2:
                    
                    self.canvas.delete(self.get(move[3], move[2]).sprite)
                    self.assign((move[2], move[3]))
                
                self.assign(click_position, selected_square)
                self.assign(self.selected_position)
                self.switch_turn()
                
                self.canvas.moveto(square_sprite, y = self.y * SPACE_SIZE, x = self.x * SPACE_SIZE)
                
                self.moves = []
                self.any_selected = False
                self.selected_position = ()
            else:
                if click_square == selected_square:
                    self.moves = []
                    self.any_selected = False
                    self.selected_position = ()
                    self.check_check()
                    return
                
                self.moves = []
                self.any_selected = False
                self.selected_position = ()
                
                black = (self.turn == 'black')
                
                if type(click_square) is Piece:
                    if click_square.black == black or (1 == 1):
                        self.any_selected = True
                        click_square.select(click_position)
                        self.draw_moves(click_square.get_moves(click_position))
                        self.selected_position = click_position
                    else:
                        self.moves = []
                        self.any_selected = False
                
        else:
            if type(click_square) is not int:
                black = (self.turn == 'black')
                if click_square.black == black or (1 == 1):
                    click_square.select(click_position)
                    self.selected_position = click_position
                    self.any_selected = True
                    self.draw_moves(click_square.get_moves(click_position))
        
        print(self.check_check())
        
    def assign(self, place, element = 0):
        self.rows[place[1]][place[0]] = element
        
    def get(self, yp = 0, xp = 0, tuple = 'empty'):
        if tuple != 'empty':
            x = tuple[0]
            y = tuple[1]
        else:
            x = xp
            y = yp
        if y not in range(0, 8) or x not in range(0, 8):
            return 'NA'
        else:
            return self.rows[y][x]
        
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
        
        if check != [False, False]:
            if check[0]:
                king = self.white_king
            else:
                king = self.black_king
            self.canvas.create_image(proportion(king), image = self.images['check'], tag = 'check', anchor = NW)
            
            black = check[1]
                            
            for row in rows:
                for square in row:
                    if type(square) is int:
                        continue
                    if square.black == black:
                        if len(square.get_moves((row.index(square), rows.index(row)))) > 0:
                            return (check, False)
        
        return (check, True)
    
            
    def draw_moves(self, moves):
        self.moves = moves
        for move in moves:
            string = 'move-circle'
            if type(self.get(move[1], move[0])) is Piece:
                string = 'move-take'
            self.canvas.create_image(move[0] * SPACE_SIZE, move[1] * SPACE_SIZE, image = self.images[string], anchor = NW, tag = 'moves')
        self.canvas.tag_raise('piece')
        
class Testpiece:
    def __init__(self, base):
        if type(base) is not int:
            
            self.type = base.type
            self.black = base.black
            self.coordinates = (base.coordinates[0] - 1, base.coordinates[1] - 1)
            self.selected = False
    
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
        
        def check_increment(x_inc, y_inc):
            x = current_x + x_inc
            y = current_y + y_inc
                        
            while self.get(y, x) != 'NA':
                            
                piece: Piece = self.get(y, x)
                if type(piece) is Piece:
                    if piece.black != self.black:
                        moves.append((x, y))
                    break
                            
                moves.append((x, y))
                x += x_inc
                y += y_inc
        
        def check_square(x, y, only_piece = False):
                    square = self.get(y, x)
                    if type(square) is not str:
                        if type(square) is int or square.black != self.black:
                            if only_piece:
                                if type(square) is Piece:
                                    moves.append((x, y))
                                    return True
                            else:
                                moves.append((x, y))
                                return True
                    return False
        
        match self.type:
            
            case 'king':
                
                check_square(current_x, current_y + 1)
                check_square(current_x + 1, current_y)
                check_square(current_x - 1, current_y)
                check_square(current_x, current_y - 1)
                check_square(current_x + 1, current_y + 1)
                check_square(current_x + 1, current_y - 1)
                check_square(current_x - 1, current_y + 1)
                check_square(current_x - 1, current_y - 1)
                
                if not self.game.w_moved[0]:
                    if not self.game.b_moved[2]:
                        if self.get(7, 1) == 0 and self.get(7, 2) == 0 and self.get(7, 3) == 0:
                            moves.append((current_x - 2, current_y))
                    if not self.game.w_moved[1]:
                        if self.get(7, 5) == 0 and self.get(7, 6) == 0:
                            moves.append((current_x + 2, current_y))
                            
                if not self.game.b_moved[0]:
                    if not self.game.b_moved[2]:
                        if self.get(0, 1) == 0 and self.get(0, 2) == 0 and self.get(0, 3) == 0:
                            moves.append((current_x - 2, current_y))
                    if not self.game.b_moved[1]:
                        if self.get(0, 5) == 0 and self.get(0, 6) == 0:
                            moves.append((current_x + 2, current_y))
            
            case 'pawn':
                if self.coordinates == coordinates:
                            
                    if check_square(current_x, current_y + 1 * multiplier):
                        check_square(current_x, current_y + 2 * multiplier)
                else:
                    check_square(current_x, current_y + 1 * multiplier)
                        
                check_square(current_x + 1 * multiplier, current_y + 1 * multiplier, True)
                check_square(current_x - 1 * multiplier, current_y + 1 * multiplier, True)
                
                if self.black:
                    en_passants = self.game.en_passants_w
                else:
                    en_passants = self.game.en_passants_b
                
                tuple = (current_x - 1 * multiplier, current_y + 1 * multiplier)
                found_passant = element_in_list(tuple, en_passants)
                if found_passant:
                    moves.append(element_in_list(tuple, en_passants, ret = True))
                    
                tuple = (current_x + 1 * multiplier, current_y + 1 * multiplier)
                found_passant = element_in_list(tuple, en_passants)
                if found_passant:
                    moves.append(element_in_list(tuple, en_passants, ret = True))
                      
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
                            
                    check_increment(1, 0)
                    check_increment(-1, 0)
                    check_increment(0, 1)
                    check_increment(0, -1)
                
                if self.type == 'bishop' or self.type == 'queen':
                    
                    check_increment(1, 1)
                    check_increment(1, -1)
                    check_increment(-1, 1)
                    check_increment(-1, -1)
        
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
            
            test_rows[move[1]][move[0]] = test_rows[current_y][current_x]
            test_rows[current_y][current_x] = 0
            if self.black:
                index = 1
            else:
                index = 0
            
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
                                    
            check = check_check(test_rows, white_king, black_king)
                
            if not check[index]:
                if move != self.game.white_king and move != self.game.black_king:
                    legal_moves.append(move)
            
        return legal_moves
    
    def get(self, yp, xp, tuple = 'empty'):
        if tuple != 'empty':
            x = tuple[0]
            y = tuple[1]
        else:
            x = xp
            y = yp
        if y not in range(0, 8) or x not in range(0, 8):
            return 'NA'
        else:
            return self.game.rows[y][x]
    
def proportion(tuple):
    return [a * SPACE_SIZE for a in tuple]
    
def element_in_list(element, list, ret = False):
    list = [a for a in list if a[0] == element[0] and a[1] == element[1]]
    if ret:
        return list[0]
    else:
        return len(list) != 0

Chess()