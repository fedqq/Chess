from tkinter import *
from Check import check_move
from PIL import Image, ImageTk
from math import floor
from Check import get

SPACE_SIZE = 110
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
        
        self.get = lambda y = 0, x = 0, tuple = 'empty': get(self.rows, y, x, tuple)
        
        def image(file_name, size = (SPACE_SIZE, SPACE_SIZE)):
            image = Image.open(f'resources/{file_name}.png')
            resized = image.resize(size)
            return ImageTk.PhotoImage(resized)
        
        self.images = {'pawn':      {False: image('pawn-w'), 
                                     True : image('pawn-b')}, 
                       'rook':      {False: image('rook-w'), 
                                     True : image('rook-b')},
                       'knight':    {False: image('knight-w'), 
                                     True : image('knight-b')}, 
                       'bishop':    {False: image('bishop-w'), 
                                     True : image('bishop-b')}, 
                       'queen':     {False: image('queen-w'), 
                                     True : image('queen-b')}, 
                       'king':      {False: image('king-w'), 
                                     True : image('king-b')},
                       
                       'move-take':         image('move-take'), 
                       'promote':           image('promote', (SPACE_SIZE * 4, SPACE_SIZE)), 
                       'end-menu':          image('lost-menu', (SPACE_SIZE * 8, SPACE_SIZE * 8)), 
                       'move-circle':       image('move-circle'), 
                       'highlight':         image('highlight'), 
                       'highlight-circle':  image('highlight-circle'), 
                       'highlight-take':    image('highlight-take'), 
                       'check':             image('check')
                       }
        
        self.turn               = 'white'
        self.playing            = False
        self.game_started       = False
        self.out                = True
        self.can_click          = True
        self.white_moved        = [False, False, False]
        self.black_moves        = [False, False, False]
        self.en_passants_w      = []
        self.en_passants_b      = []
        self.moves              = []
            
        self.canvas = Canvas(self.window, bg = MAIN_BG, width = SPACE_SIZE * 8, height = SPACE_SIZE * 8, bd = 0, relief = FLAT)
        self.label = Label(self.window, text = 'White: \t\tBlack: \t\t', bg = MAIN_BG, font = ('times new roman', 27), fg = 'white')
        self.canvas.tag_lower('bg')
            
        def change(b):
            self.out = b
            
        self.canvas.bind('<Enter>',     lambda *args: change(False))
        self.canvas.bind('<Leave>',     lambda *args: change(True))
        self.window.bind('<Motion>',    self.motion)
        self.window.bind('<Button-1>',  self.click)
        self.window.bind('<Up>',        lambda e: self.lose_game())
        
        self.input_strings = [[StringVar(), '1200'], [StringVar(), '500']]
        font = ('times new roman', 20)
        
        self.time_label = Label(self.window, text = 'Time: ', font = font, bg = MAIN_BG, fg = 'white')
        self.time_input = Entry(self.window, bg = MAIN_BG, fg = 'white', bd = 0, font = font, textvariable = self.input_strings[0][0], width = 7)
        self.time_input.insert(0, f'{BASE_TIME}')
        
        self.increment_label = Label(self.window, text = ' + ', font = font, bg = MAIN_BG, fg = 'white')
        self.increment_input = Entry(self.window, bg = MAIN_BG, fg = 'white', bd = 0, font = font, textvariable = self.input_strings[1][0], width = 7)
        self.increment_input.insert(0, f'{INCREMENT}')
        
        self.rows = [[0 for _ in range(0, 8)] for _ in range(0, 8)]
            
        i = 0
        for row in range(0, 8):
            for column in range(0, 8):
                if ((column + (row * 8)) + i) % 2 == 0:
                    (x, y) = proportion(column, row)
                    self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill = SQUARE_BG, outline = '', tag = 'bg')
            i += 1
            
        self.input_strings[0][0].trace('w', lambda *args: self.check_text(True))
        self.input_strings[1][0].trace('w', lambda *args: self.check_text(False))
        
        self.canvas.create_text(500, 400, text = 'Chess\nPress anywhere to play', font = ('times new roman', 55), justify = CENTER, tag = 'title')

        self.canvas.pack(side = BOTTOM)
        self.label.pack(side = RIGHT)
        self.time_label.pack(side = LEFT)
        self.time_input.pack(side = LEFT)
        self.increment_label.pack(side = LEFT)
        self.increment_input.pack(side = LEFT)
        
        self.window.mainloop()
        
    def show_promote_menu(self, position, black = False):
        pos = (2, 3.5)
        self.canvas.create_image(proportion(pos), image = self.images['promote'], anchor = NW, tag = 'pro')
        
        queen   = self.canvas.create_image(proportion(       pos        ), image = self.images['queen' ][black], anchor = NW, tag = 'pro')
        rook    = self.canvas.create_image(proportion(pos[0] + 1, pos[1]), image = self.images[ 'rook' ][black], anchor = NW, tag = 'pro')
        bishop  = self.canvas.create_image(proportion(pos[0] + 2, pos[1]), image = self.images['bishop'][black], anchor = NW, tag = 'pro')
        knight  = self.canvas.create_image(proportion(pos[0] + 3, pos[1]), image = self.images['knight'][black], anchor = NW, tag = 'pro')
        
        self.canvas.tag_bind(queen , '<Button-1>', lambda e: select('queen' ))
        self.canvas.tag_bind(rook  , '<Button-1>', lambda e: select( 'rook' ))
        self.canvas.tag_bind(bishop, '<Button-1>', lambda e: select('bishop'))
        self.canvas.tag_bind(knight, '<Button-1>', lambda e: select('knight'))
        
        self.can_click = False
        
        def select(type):
            self.canvas.delete('pro')
            self.can_click = True
            self.canvas.delete(self.rows[position[1]][position[0]].sprite)
            self.rows[position[1]][position[0]] = 0
            self.rows[position[1]][position[0]] = Piece(position, self, black, type)
        
    def check_text(self, one):
        if one:
            test = self.input_strings[0]
        else:
            test = self.input_strings[1]
        
        if (test[0].get().isdigit() or test[0].get() == '') and not self.playing and not len(test[0].get()) > 6:
            test[1] = test[0].get()
        else:
            test[0].set(test[1])
        
    def start_game(self):
        
        self.canvas.delete('title')
        
        if self.input_strings[0][1].strip() == '' or self.input_strings[1][1].strip() == '':
            return
        else:
            self.base = int(self.input_strings[0][1])
            self.increment = int(self.input_strings[1][1])
        
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
                     [Piece((number, 0), self, True, pieces[number]) for number in range(8)], 
                     [Piece((number, 1), self, True) for number in range(8)], 
                     [0 for _ in range(0, 8)],
                     [0 for _ in range(0, 8)], 
                     [0 for _ in range(0, 8)], 
                     [0 for _ in range(0, 8)], 
                     [Piece((number, 6), self, False) for number in range(8)],
                     [Piece((number, 7), self, False, pieces[number]) for number in range(8)]
                    ]
        
    def restart(self, *args):
        self.start_game()
        
    def lose_game(self, winner = 'Draw'):
        self.playing = False
        self.canvas.create_image(0, 0, image = self.images['end-menu'], anchor = NW, tag = 'title')
        text = winner
        if winner != 'draw':
            text = f'{winner} Won\nBy Checkmate'
        
        self.canvas.create_text(proportion(4, 4), text = text, font = ('times new roman', 54), fill = 'white', tag = 'title', justify = CENTER)
        
    def motion(self, event):
            self.canvas.delete('hover')
            x = event.x - event.x % SPACE_SIZE
            x = int(x / SPACE_SIZE)
            y = event.y - event.y % SPACE_SIZE
            y = int(y / SPACE_SIZE)
            
            if x > 7:
                x = 7
            elif x < 0:
                x = 0
                
            if y > 7:
                y = 7
            elif y < 0:
                y = 0
                
            self.mouse_position = (x, y)
                
            if len(self.moves) != 0:
                
                if element_in_list(self.mouse_position, self.moves):
                    if type(self.get(tuple = self.mouse_position)) is Piece:
                        self.canvas.create_image(proportion(self.mouse_position), image = self.images['highlight-take'], anchor = NW, tag = 'hover')
                    else:
                        self.canvas.create_image(proportion(self.mouse_position), image = self.images['highlight-circle'], anchor = NW, tag = 'hover')
                        
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
        
        if not self.can_click: 
            return       
        
        self.canvas.delete('moves', 'check', 'hover', 'highlight')
        
        if not self.timer_started:
            self.timer_started = True
            self.tick_timer()
         
        mouse_position = self.mouse_position
        assign = self.assign
        get = self.get
        
        click_square: Piece = get(tuple = mouse_position)
        
        if self.any_selected:
            selected_square: Piece = get(tuple = self.selected_position)
            
            if element_in_list(mouse_position, self.moves):
                
                square_sprite = selected_square.sprite
                
                if type(click_square) is Piece:
                    self.canvas.delete(click_square.sprite)
                
                match selected_square.type:
                    case 'king':
                        if selected_square.black:
                            self.black_moves[0] = True
                            self.black_king = mouse_position
                        else:
                            self.white_moved[0] = True
                            self.white_king = mouse_position
                        
                        if selected_square.black:
                            row = 0
                        else:
                            row = 7
                            
                        if self.mouse_position[0] - self.selected_position[0] == 2:
                            
                            self.canvas.move(get(row, 7).sprite, SPACE_SIZE * -2, 0)
                            assign((5, row), get(row, 7))
                            assign((7, row))
                            
                        elif self.mouse_position[0] - self.selected_position[0] == -2:
                            
                            self.canvas.move(get(row, 0).sprite, SPACE_SIZE * 3, 0)
                            assign((3, row), get(row, 0))
                            assign((0, row))
                                
                    case 'pawn':
                        
                        if abs(self.selected_position[1] - mouse_position[1]) == 2:
                            object = (self.selected_position[0], int((self.selected_position[1] + mouse_position[1]) / 2), mouse_position[0], mouse_position[1])
                            if selected_square.black:
                                self.en_passants_b.append(object)
                            else:
                                self.en_passants_w.append(object)
                                
                        if mouse_position[1] == (7 if selected_square.black else 0):
                            self.show_promote_menu(mouse_position, selected_square.black)
                                
                    case _:
                        if 'rook' in selected_square.type:
                            if selected_square.black:
                                if selected_square.type == 'lrook':
                                    self.black_moves[1] = True
                                elif selected_square.type == 'rrook':
                                    self.black_moves[2] = True
                            else:
                                if selected_square.type == 'lrook':
                                    self.white_moved[1] = True
                                elif selected_square.type == 'rrook':
                                    self.white_moved[2] = True
                            
                move = element_in_list(mouse_position, self.moves, True)
                if len(move) > 2:
                    
                    self.canvas.delete(self.get(move[3], move[2]).sprite)
                    assign((move[2], move[3]))
                
                assign(mouse_position, selected_square)
                assign(self.selected_position)
                self.switch_turn()
                
                self.canvas.moveto(square_sprite, y = mouse_position[1] * SPACE_SIZE, x = mouse_position[0] * SPACE_SIZE)
                
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
                    if click_square.black == black or 1 == 1:
                        self.any_selected = True
                        click_square.select(mouse_position)
                        self.draw_moves(click_square.get_moves(mouse_position))
                        self.selected_position = mouse_position
                    else:
                        self.moves = []
                        self.any_selected = False
                
        else:
            if type(click_square) is not int:
                black = (self.turn == 'black')
                if click_square.black == black or 1 == 1:
                    click_square.select(mouse_position)
                    self.selected_position = mouse_position
                    self.any_selected = True
                    self.draw_moves(click_square.get_moves(mouse_position))
                    
        self.check_check()
        
    def assign(self, place, element = 0):
        self.rows[place[1]][place[0]] = element
        
    def tick_timer(self):
        if self.turn == 'white' or 1 == 1:
            self.timer[0] -= 1
        else:
            self.timer[1] -= 1
        
        white = f'{floor(self.timer[0]/60)}:{self.timer[0] % 60}'
        black = f'{floor(self.timer[1]/60)}:{self.timer[1] % 60}'
        self.label.configure(text = f'White: {white}\tBlack: {black}\t')
        
        self.window.after(1000, self.tick_timer)
        
    def check_check(self) -> tuple:
        self.canvas.delete('check')
        rows = self.rows
        
        check = check_move(self.rows)
        
        if check != [False, False]:
            
            self.canvas.create_image(   
                                        proportion(self.white_king if check[0] else self.black_king), 
                                        image = self.images['check'], 
                                        tag = 'check', 
                                        anchor = NW
                                    )
                
        moveable = [False, False]
                                
        for row in rows:
            for square in row:
                if type(square) is int:
                    continue
                if square.black:
                    if len(square.get_moves((row.index(square), rows.index(row)))) > 0:
                        moveable[1] = True
                        break
             
        for row in rows:
            for square in row:
                if type(square) is int:
                    continue
                if not square.black:
                    if len(square.get_moves((row.index(square), rows.index(row)))) > 0:
                        moveable[0] = True
                        break
                    
        print(moveable, check)
        
        if not moveable[0]:
            if check[0]: 
                self.lose_game('Black')
                return
            else:
                self.lose_game()
        if not moveable[1]:
            if check[1]:
                self.lose_game('White')
                return
            else:
                self.lose_game()
        
        
    
    def draw_moves(self, moves):
        self.moves = moves
        for move in moves:
            string = 'move-circle'
            if type(self.get(move[1], move[0])) is Piece:
                string = 'move-take'
            self.canvas.create_image(move[0] * SPACE_SIZE, move[1] * SPACE_SIZE, image = self.images[string], anchor = NW, tag = 'moves')
        self.canvas.tag_raise('piece')
    
class Piece:
    def __init__(self, position = '', game: Chess = None, black = False, piece_type = 'pawn'):
        self.type = piece_type
        self.game = game
        self.black = black
        self.start_position = (position[0], position[1])
        self.get = lambda y = 0, x = 0, tuple = 'empty': get(game.rows, y, x, tuple)
        self.sprite = self.game.canvas.create_image(proportion(self.start_position), image = self.game.images['rook' if 'rook' in self.type else self.type][self.black], anchor = NW, tag = 'piece')
            
    def select(self, position):
        self.game.canvas.create_image(proportion(position), image = self.game.images['highlight'], anchor = NW, tag = 'highlight')
        self.game.canvas.tag_raise('piece')
        
    def get_moves(self, position) -> list:
        moves = []
        multiplier = -1
        if self.black:
            multiplier = 1
            
        x = position[0]
        y = position[1]
        
        rows = self.game.rows
        
        def check_increment(x_inc, y_inc):
            test_x = x + x_inc
            test_y = y + y_inc
                        
            while self.get(test_y, test_x) != 'NA':
                            
                piece: Piece = self.get(test_y, test_x)
                if type(piece) is Piece:
                    if piece.black != self.black:
                        moves.append((test_x, test_y))
                    break
                            
                moves.append((test_x, test_y))
                test_x += x_inc
                test_y += y_inc
        
        def check_square(x, y, only_piece = False, only_empty = False) -> bool:
                    square = self.get(y, x)
                    if type(square) is not str and (type(square) is int or square.black != self.black):
                        if only_piece and not only_empty:
                            if type(square) is Piece:
                                moves.append((x, y))
                                return True
                        elif only_empty and not only_piece:
                            if type(square) is not Piece:
                                moves.append((x, y))
                                return True
                        else:
                            moves.append((x, y))
                            return True
                    return False
                
        pos = (x, y)
        
        match self.type:
            
            case 'king':
                
                check_square(x, y + 1)
                check_square(x + 1, y)
                check_square(x - 1, y)
                check_square(x, y - 1)
                check_square(x + 1, y + 1)
                check_square(x + 1, y - 1)
                check_square(x - 1, y + 1)
                check_square(x - 1, y - 1)
                
                if self.black:
                    moved = self.game.black_moves
                    row = 0
                else:
                    moved = self.game.white_moved
                    row = 7
                    
                g = lambda *args: self.get(args[0], args[1])
                check = lambda i, n_pos = pos: check_move(rows, pos, n_pos, 'b' if self.black else 'w')[i] == False
                
                if not moved[0]:
                    if not moved[2]:
                        if g(row, 1) == 0 and g(row, 2) == 0 and g(row, 3) == 0 and g(row, 0) != 0:
                            
                            if check(1) and check(1, (row, 1)) and check(1, (row, 2)) and check(1, (row, 3)):
                                
                                moves.append((x - 2, y))
                            
                    if not moved[1]:
                        if g(row, 5) == 0 and g(row, 6) == 0 and g(row, 7) != 0:
                            if check(0) and check(0, (row, 5)) and check(0, (row, 6)):
                                moves.append((x + 2, y))
            
            case 'pawn':
                if self.start_position == position:
                    if check_square(x, y + 1 * multiplier, only_empty = True) and not check_move(rows, pos, (x, y + 1 * multiplier))[1 if self.black else 0]:
                        check_square(x, y + 2 * multiplier, only_empty = True)
                        
                else:
                    check_square(x, y + 1 * multiplier, only_empty = True)
                        
                check_square(x + 1 * multiplier, y + 1 * multiplier, True)
                check_square(x - 1 * multiplier, y + 1 * multiplier, True)
                
                if self.black:
                    en_passants = self.game.en_passants_w
                else:
                    en_passants = self.game.en_passants_b
                
                tuple = (x - 1 * multiplier, y + 1 * multiplier)
                found_passant = element_in_list(tuple, en_passants)
                if found_passant:
                    moves.append(element_in_list(tuple, en_passants, ret = True))
                    
                tuple = (x + 1 * multiplier, y + 1 * multiplier)
                found_passant = element_in_list(tuple, en_passants)
                if found_passant:
                    moves.append(element_in_list(tuple, en_passants, ret = True))
                      
            case 'knight':
                
                for move in ((2, 1), (1, 2), (-2, 1), (2, -1), (-2, -1), (-1, 2), (-1, -2), (1, -2)):
                    piece = self.get(y + move[0], x + move[1])
                    if piece != 'NA':
                        if type(piece) is Piece:
                            if piece.black != self.black:
                                moves.append((x + move[1], y + move[0]))
                        else:
                            moves.append((x + move[1], y + move[0]))
                            
            case _:
                if 'rook' in self.type or self.type == 'queen':
                            
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
            if not check_move(rows, (x, y), move)[1 if self.black else 0]:
                if type(self.get(tuple = move)) is not int:
                    if self.get(tuple = move).type != 'king':
                        legal_moves.append(move)
                else:
                    legal_moves.append(move)
            
        return legal_moves
    
def proportion(*args) -> list:
    return [a * SPACE_SIZE for a in (args[0] if len(args) == 1 else args)]
    
def element_in_list(element, list, ret = False) -> list | bool:
    list = [a for a in list if a[0] == element[0] and a[1] == element[1]]
    if ret:
        return list[0]
    else:
        return len(list) != 0
    
Chess()