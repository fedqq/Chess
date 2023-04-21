from tkinter import *
from tkinter import ttk
import tkinter
from Check import check_move
from PIL import Image, ImageTk
from math import floor
from Check import get
import sv_ttk
from ctypes import windll

windll.shcore.SetProcessDpiAwareness(1)

SPACE_SIZE = None #To be set after the window is created, as a fraction of the screen height
MAIN_BG = '#1C1C1C'
BACKGROUND = '#686868'
FRONT_COLOR = '#E6F4F4'
BASE_TIME = 1200
INCREMENT = 500
KNIGHT_MOVES = ((2, 1), (1, 2), (-2, 1), (2, -1), (-2, -1), (-1, 2), (-1, -2), (1, -2), False)
KING_MOVES = ((0, 1), (1, 0), (1, 1), (-1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1), False)
ROOK_MOVES = ((-1, 0), (1, 0), (0, -1), (0, 1), True)
BISHOP_MOVES = ((-1, -1), (1, -1), (-1, 1), (1, 1), True)
DEBUG = True


class Chess:  
    def __init__(self) -> None:
        global SPACE_SIZE
        
        self.turn               = 'white'
        self.playing            = False
        self.paused             = False
        self.flipped            = False
        self.promo_on           = False
        self.game_started       = False
        self.any_selected       = False
        self.flip_on            = True
        self.out                = True
        self.can_click          = True
        self.white_moved        = [False, False, False]
        self.black_moved        = [False, False, False]
        self.en_passants_w      = []
        self.en_passants_b      = []
        self.moves              = []
        self.move_counter       = 0
        self.rows               = [[0,0,0,0,0,0,0,0] * 8]
        self.selected_position  = (0, 0)
        self.game_positions     = {}
        self.images             = {}
        
        self.window             = Tk()
        
        SPACE_SIZE = int(self.window.winfo_screenheight() / 10)
        
        self.canvas = Canvas(self.window, bg = BACKGROUND, width = SPACE_SIZE * 8, height = SPACE_SIZE * 8, bd = 0, relief = FLAT)
        self.options = ttk.Frame(self.window, width = SPACE_SIZE * 8)
        self.labels =  ttk.Frame(self.window, width = SPACE_SIZE * 8)
        
        self.white_label = ttk.Label(self.labels, text = 'W: \tPoints: ', font = ('Segoe UI', 22))
        self.white_label.pack(side = LEFT)
        
        self.black_label = ttk.Label(self.labels, text = 'B: \tPoints: \t', font = ('Segoe UI', 22))
        self.black_label.pack(side = RIGHT)
        
        self.input_strings = [[StringVar(), '1200'], [StringVar(), '500']]
        self.input_strings[0][0].trace('w', lambda *args: self.check_text(True))
        self.input_strings[1][0].trace('w', lambda *args: self.check_text(False))
        
        self.time_label = ttk.Label(self.options, text = 'Time: ')
        self.time_input = ttk.Entry(self.options, textvariable = self.input_strings[0][0], width = 7)
        self.time_input.insert(0, str(BASE_TIME))
        self.time_label.pack(side = LEFT)
        self.time_input.pack(side = LEFT)
        
        self.increment_label = ttk.Label(self.options, text = ' + ')
        self.increment_input = ttk.Entry(self.options, textvariable = self.input_strings[1][0], width = 7)
        self.increment_input.insert(0,str(INCREMENT))
        self.increment_label.pack(side = LEFT)
        self.increment_input.pack(side = LEFT)
        
        def toggle():
            self.flip_on = b_var.get()
            
        def draw():
            self.lose_game(method = '\nAgreement')
            
        b_var = BooleanVar()
        b_var.set(True)
        self.flip_toggle = ttk.Checkbutton(self.options, text = 'Flipping', command = toggle, variable = b_var)
        self.flip_toggle.pack(side = RIGHT, padx = 10)
        
        self.draw_btn = ttk.Button(self.options, command = draw, text = 'Draw', style = 'Accent.TButton')
        self.draw_btn.pack(side = RIGHT)
        self.draw_btn.configure(state = 'disabled')
        
        self.labels.pack(expand = True, fill = BOTH)
        self.canvas.pack(expand = False)
        self.options.pack(expand = True, fill = BOTH)
        
        sv_ttk.set_theme('dark')
        style = ttk.Style(self.window)
        style.theme_use('sun-valley-dark')
        style.configure('TCheckbutton', font = ("Segoe UI", 15))
        style.configure('TEntry',       font = ("Segoe UI", 15))
        style.configure('TLabel',       font = ("Segoe UI", 15))
        
        self.get     = lambda y = 0, x = 0, tuple = 'empty': get(self.rows, y, x, tuple)
        self.update  = self.canvas.update
        
        self.window.title('Chess')
        self.window.resizable(False, False)
        self.window.configure(bg = MAIN_BG, padx = 20, pady = 0)
        
        def img(file_name, pre = 'pieces', size = (SPACE_SIZE, SPACE_SIZE)):
            image = Image.open(f'resources/{pre}/{file_name}.png')
            return ImageTk.PhotoImage(image.resize(size, Image.LANCZOS))
        
        def add_piece(*args):
            for name in args:
                self.images[name] = {False: img(name + '-w'), True: img(name + '-b')}

        def add_image(name, size = (SPACE_SIZE, SPACE_SIZE), pre = 'other'):
            pass
            
        def add_image(*args):
            for arg in args:
                if type(arg) is not list:
                    arg = [arg]
                if len(arg) < 2:
                    arg.append((SPACE_SIZE, SPACE_SIZE))
                if len(arg) < 3:
                    arg.append('other')
                name = arg[0]
                size = arg[1]
                pre = arg[2]
                self.images[name] = img(name, pre, size)
        
        add_piece('pawn', 'rook', 'bishop', 'knight', 'queen', 'king')
        add_image('move-take', 'move-circle', 'highlight-c', 'highlight-t', 'check', 'last', 'highlight')
        add_image(['promote', (SPACE_SIZE * 4, SPACE_SIZE)], ['end-menu', (SPACE_SIZE * 8, SPACE_SIZE * 8)])
        
        for row in range(0, 8):
            for column in range(0, 8):
                if (column + row * 8 + row) % 2 == 0:
                    (x, y) = proportion(column, row)
                    self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill = FRONT_COLOR, outline = '', tag = 'bg')
            
        self.canvas.tag_raise('piece')
            
        def change(b):
            self.out = b
            
        self.canvas.bind('<Enter>',     lambda *args: change(False))
        self.canvas.bind('<Leave>',     lambda *args: change(True))
        self.window.bind('<Motion>',    self.motion)
        self.window.bind('<Button-1>',  self.click)

        self.window.mainloop()
        
    def create_image(self, position, image, tag = 'piece', raise_p = True):
            ret = self.canvas.create_image(proportion(position), image = image, anchor = NW, tag = tag)
            if raise_p:
                self.canvas.tag_raise('piece')
            return ret
        
    def show_promote_menu(self, position, black = False):
        self.promo_on = True
        pos = (2, 3.5)
        self.create_image(pos, self.images['promote'], tag = 'pro')
        
        queen       = self.create_image(        pos         , self.images['queen' ][black], tag = 'pro')
        rook        = self.create_image((pos[0] + 1, pos[1]), self.images[ 'rook' ][black], tag = 'pro')
        bishop      = self.create_image((pos[0] + 2, pos[1]), self.images['bishop'][black], tag = 'pro')
        knight      = self.create_image((pos[0] + 3, pos[1]), self.images['knight'][black], tag = 'pro')
        
        self.canvas.tag_bind(queen  , '<Button-1>', lambda e: select('queen' ))
        self.canvas.tag_bind(rook   , '<Button-1>', lambda e: select( 'rook' ))
        self.canvas.tag_bind(bishop , '<Button-1>', lambda e: select('bishop'))
        self.canvas.tag_bind(knight , '<Button-1>', lambda e: select('knight'))
        
        self.can_click = False
        
        def select(type):
            self.canvas.delete('pro')
            self.can_click = True
            self.canvas.delete(self.get(tuple = position).sprite)
            self.assign(position)
            self.assign(position, Piece(position, self, black, type))
            self.promo_on = False
            if self.flip_on:
                self.flip()
        
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
            
        self.increment_input.configure(state = 'disabled')
        self.time_input.configure(state = 'disabled')
        self.draw_btn.configure(state = 'normal')
        
        self.canvas.delete('piece', 'check', 'highlight', 'hover', 'last')
        
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
        
        self.game_positions = {self.get_code(): 1}
          
    def restart(self, *args):
        self.start_game()
        
    def lose_game(self, winner = 'Draw', method = 'Checkmate'):
        if not self.playing:
            return
        self.playing = False
        self.create_image((0, 0), self.images['end-menu'], 'title', False)
        if winner != 'Draw':
            text = f'{winner} Won\nBy {method}'
            symbol  ='♚' if winner == 'black' else '♔'
        else:
            text = f'{winner} by {method}'
            symbol = '♔-♚'
        
        self.canvas.create_text(proportion(4, 3), text = text, font = ('Segoe UI', 54), fill = 'white', tag = 'title', justify = CENTER)
        self.canvas.create_text(proportion(4, 5), text = symbol, font = ('calibri', 100), fill = 'white', tag = 'title', justify = CENTER)
        
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
                    test = type(self.get(tuple = self.mouse_position)) is Piece
                    text = f"highlight-{'t' if test else 'c'}"
                    self.create_image(self.mouse_position, self.images[text], 'hover')
                    
    def count_advantage(self):
        scores = [0, 0]
        for row in self.rows:
            for square in row:
                if type(square) is int:
                    continue
                
                num = 0
                if square.black:
                    num = 1
                    
                short = square.type[:2]
                if short in 'knbi':
                    scores[num] += 3
                elif short in 'rr lr':
                    scores[num] += 5
                elif short == 'ki':
                    scores[num] += 4
                elif short == 'qu':
                    scores[num] += 9
                else:
                    scores[num] += 1
                    
        if scores[0] > scores[1]:
            return scores[0] - scores[1], 'w'
        elif scores[0] < scores[1]:
            return scores[1] - scores[0], 'b'
        else:
            return 0, 'd'
               
    def switch_turn(self):
        
        if self.turn == 'white':
            self.turn = 'black'
            self.timer[1] += INCREMENT
            if not DEBUG:
                self.en_passants_b.clear()
        else:
            self.turn = 'white'
            self.timer[0] += INCREMENT
            if not DEBUG:
                self.en_passants_w.clear()
        
    def click(self, event):
        if not self.playing:
            if not self.out:
                self.start_game()
            return
        
        if not self.can_click: 
            return     
        
        canvas = self.canvas  
        
        canvas.delete('moves', 'hover', 'highlight')
        
        if not self.timer_started:
            self.timer_started = True
            self.tick_timer()
         
        mouse_position = self.mouse_position
        select_position = self.selected_position 
        
        assign = self.assign
        get = self.get
        
        click_square: Piece = get(tuple = mouse_position)
        
        if self.any_selected:
           
            selected_square: Piece = get(tuple = select_position)
            
            if element_in_list(mouse_position, self.moves):
                
                square_sprite = selected_square.sprite
                
                if type(click_square) is Piece:
                    self.move_counter = 0
                    canvas.delete(click_square.sprite)
                    
                def num(n):
                            if self.flipped:
                                return 7 - n
                            else:
                                return n
                
                match selected_square.type:
                    case 'king':
                        if selected_square.black:
                            self.black_king = mouse_position
                        else:
                            self.white_king = mouse_position
                        
                        if selected_square.black:
                            row = num(0)
                        else:
                            row = num(7)
                            
                        multi = -1 if self.flipped else 1
                        
                        if mouse_position[0] - select_position[0] == (2 * multi):
                            
                            canvas.move(get(row, num(7)).sprite, SPACE_SIZE * -2 * multi, 0)
                            assign((num(5), row), get(row, num(7)))
                            assign((num(7), row))
                            
                        elif mouse_position[0] - select_position[0] == (-2 * multi):
                            
                            canvas.move(get(row, num(0)).sprite, SPACE_SIZE * 3 * multi, 0)
                            assign((num(3), row), get(row, num(0)))
                            assign((num(0), row))
                                
                    case 'pawn':
                        
                        self.move_counter = 0
                        
                        if abs(select_position[1] - mouse_position[1]) == 2:
                            object = (select_position[0], int((select_position[1] + mouse_position[1]) / 2), mouse_position[0], mouse_position[1])
                            if selected_square.black:
                                self.en_passants_b.append(object)
                            else:
                                self.en_passants_w.append(object)
                                
                        if mouse_position[1] == (num(7) if selected_square.black else num(0)):
                            self.show_promote_menu(mouse_position, selected_square.black)
                                
                    case _:
                        if 'rook' in selected_square.type:
                            if selected_square.black:
                                if selected_square.type == 'lrook':
                                    self.black_moved[1] = True
                                elif selected_square.type == 'rrook':
                                    self.black_moved[2] = True
                            else:
                                if selected_square.type == 'lrook':
                                    self.white_moved[1] = True
                                elif selected_square.type == 'rrook':
                                    self.white_moved[2] = True
                            
                move = element_in_list(mouse_position, self.moves, ret = True)
                    
                if len(move) > 2:
                    canvas.delete(self.get(move[3], move[2]).sprite)
                    assign((move[2], move[3]))
                
                assign(mouse_position, selected_square)
                assign(self.selected_position)
                selected_square.move()
                
                canvas.delete('last')
                
                canvas.moveto(square_sprite, y = mouse_position[1] * SPACE_SIZE, x = mouse_position[0] * SPACE_SIZE)
                self.last_move = (select_position, mouse_position)
                
                if not self.flipped:
                    self.test_draw()
                
                if self.flip_on:
                    self.update()
                    self.pause_timer()
                    self.can_click = False
                    self.flip()
                    if self.flipped:
                        self.test_draw()
                else:
                    self.create_image(self.last_move[0], self.images['last'], 'last')
                    self.create_image(self.last_move[1], self.images['last'], 'last')
                    
                self.update()
                
                self.moves = []
                self.any_selected = False
                select_position = ()
                self.test_check()
                
            else:
                self.moves = []
                self.any_selected = False
                self.selected_position = ()
                
                if mouse_position == select_position:
                    return
                
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
        
    def assign(self, place, element = 0):
        self.rows[place[1]][place[0]] = element
        
    def get_code(self):
        
        string = ''
        
        for row in self.rows:
            for square in row:
                if type(square) is int:
                    string += '0'
                else:
                    string += square.string()
                    
        if len(self.en_passants_b) < 1:
            string += '0'
        
        for e in self.en_passants_b:
            string += f'{e[0]}{e[1]}{e[2]}{e[3]}'
            
        if len(self.en_passants_w) < 1:
            string += '0'
        
        for e in self.en_passants_w:
            string += f'{e[0]}{e[1]}{e[2]}{e[3]}'
        
        for moved in (self.black_moved, self.white_moved):
            
            for b in moved:
                string += ('1' if b else '0')
            
        string += f'{self.turn[0]}'
        
        return string
    
    def pause_timer(self):
        self.paused = True
        
    def tick_timer(self):
        if self.paused:
            self.window.after(1000, self.tick_timer)
            
        if self.turn == 'white' or 1 == 1:
            self.timer[0] -= 1
        else:
            self.timer[1] -= 1
        
        white = f'{floor(self.timer[0]/60)}:{self.timer[0] % 60}'
        black = f'{floor(self.timer[1]/60)}:{self.timer[1] % 60}'
        score = self.count_advantage()
        
        black_s, white_s = '+0', '+0'
        if score[1] == 'b':
            black_s = f'+{score[0]}'
        elif score[1] == 'w':
            white_s = f'+{score[0]}'
        
        self.white_label.configure(text = f'W: {white}\tPoints: {white_s}')
        self.black_label.configure(text = f'B: {black}\tPoints: {black_s}')
        self.window.after(1000, self.tick_timer)
        
    def test_draw(self):
        
        self.move_counter += 1
        code = self.get_code()
                
        if code in self.game_positions:
            self.game_positions[code] += 1
        else:
            self.game_positions[code] = 1
            
        if self.game_positions[code] == 3:
            self.lose_game(method = '\nThreefold Repetition')
            
        if self.move_counter == 100:
            self.lose_game(method = '\nFifty Move Rule')
        
    def test_check(self) -> tuple:
        self.canvas.delete('check')
        rows = self.rows
        
        check = check_move(self.rows, flipped = self.flipped)
        
        if check != [False, False]:
            
            self.create_image(self.white_king if check[0] else self.black_king, self.images['check'], 'check')
                
        moveable = [False, False]
        
        self.canvas.pack()
                                
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
                self.lose_game(method = 'Stalemate')
    
    def draw_moves(self, moves):
        self.moves = moves
        for move in moves:
            string = 'move-circle'
            if type(self.get(move[1], move[0])) is Piece:
                string = 'move-take'
            self.create_image(move[:2], self.images[string], 'moves')
            
    def flip(self):
        
        if self.promo_on:
            return
        
        self.moves = []
        
        self.canvas.itemconfig('piece', state = 'hidden')
        
        for row in self.rows:
            for square in row:
                if not type(square) is int:
                    self.canvas.moveto(square.sprite, x = (7 - row.index(square)) * SPACE_SIZE, y = (7-self.rows.index(row)) * SPACE_SIZE)
                    self.canvas.itemconfigure(square.sprite, state = 'normal')
                    self.update()
                    
        self.paused = False
        self.flipped = not self.flipped
        self.rows = [row[::-1] for row in self.rows][::-1]
            
        self.en_passants_w = [[7 - elem for elem in p] for p in self.en_passants_w]
        self.en_passants_b = [[7 - elem for elem in p] for p in self.en_passants_b]
         
        self.white_king = [7 - elem for elem in self.white_king]
        self.black_king = [7 - elem for elem in self.black_king]
        
        self.last_move = [[7 - elem for elem in p] for p in self.last_move]
        
        self.create_image(self.last_move[0], self.images['last'], 'last')
        self.create_image(self.last_move[1], self.images['last'], 'last')
        
        self.can_click = True
        
        self.update()
        
        self.test_check()
        self.update()
        
        self.test_draw()
    
class Piece:
    def __init__(self, position = '', game: Chess = None, black = False, piece_type = 'pawn'):
        self.type = piece_type
        self.game = game
        self.black = black
        self.moved = False
        self.start_position = (position[0], position[1])
        self.get = lambda y = 0, x = 0, tuple = 'empty': get(game.rows, y, x, tuple)
        self.sprite = self.game.create_image(position, self.game.images['rook' if 'rook' in self.type else self.type][self.black])
            
    def select(self, position):
        self.game.create_image(position, self.game.images['highlight'], 'highlight')
        
    def move(self):
        self.moved = True
        
    def get_moves(self, position) -> list:
        
        def flip(list):
                    if self.game.flipped:
                        return [7 - n  for n in list]
                    else:
                        return list
        
        moves = []
        
        multiplier = -1
        if self.black:
            multiplier = 1
        
        pos = flip(position)
        x, y = pos
        
        game = self.game
        
        test_rows = game.rows
        if game.flipped:
            test_rows = [row[::-1] for row in test_rows][::-1]
        
        g = lambda y, x: get(test_rows, y, x)
        
        def check_increment(x_inc, y_inc):
            test_x = x + x_inc
            test_y = y + y_inc
                        
            while g(test_y, test_x) != 'NA':
                            
                piece: Piece = g(test_y, test_x)
                if type(piece) is Piece:
                    if piece.black != self.black:
                        add_move((test_x, test_y))
                    break
                            
                add_move((test_x, test_y))
                test_x += x_inc
                test_y += y_inc
        
        def check_square(x, y, only_piece = False, only_empty = False) -> bool:
                    square = g(y, x)
                    if type(square) is not str and (type(square) is int or square.black != self.black):
                        if only_piece and not only_empty:
                            if type(square) is Piece:
                                add_move((x, y))
                                return True
                        elif only_empty and not only_piece:
                            if type(square) is not Piece:
                                add_move((x, y))
                                return True
                        else:
                            add_move((x, y))
                            return True
                    return False
        
        def add_move(move):
            moves.append(flip(move))
        
        match self.type:
            
            case 'king':
                
                possible_moves = KING_MOVES
                
                
                check = lambda index, n_pos = pos: check_move(test_rows, pos, n_pos, 'white' if not self.black else 'black', self.game.flipped)[index] == False
                n_check = lambda n_pos = pos: check_move(test_rows, pos, flip(n_pos), 'all', self.game.flipped)
                
                rooks_moved = [True, True]
                
                rrook_pos = (0, y)
                lrook_pos = (7, y)
                        
                rrook = g(rrook_pos[1], rrook_pos[0])
                if type(rrook) is not int:
                    if not rrook.moved:
                        rooks_moved[1] = False
                        
                lrook = g(lrook_pos[1], lrook_pos[0])
                if type(lrook) is not int:
                    if not lrook.moved:
                        rooks_moved[0] = False     
                    
                num = int(self.black == True)
                        
                if not self.moved:
                    if not rooks_moved[0]:
                        if g(y, x - 1) == 0 and g(y, x - 2) == 0 and g(y, x - 3) == 0:
                            if check(num) and check(num, (x - 1, y)) and check(num, (x - 2, y)):
                                add_move((x - 2, y))
                                
                    if not rooks_moved[1]:
                        if g(y, x + 1) == 0 and g(y, x + 2) == 0:
                            if check(num) and check(num, (x + 1, y)):
                                add_move((x + 2, y))
                                
            
            case 'pawn':
                if not self.moved:
                    if check_square(x, y + multiplier, only_empty = True) and not check_move(test_rows, pos, (x, y + multiplier), flipped = self.game.flipped)[1 if self.black else 0]:
                        check_square(x, y + 2 * multiplier, only_empty = True)
                        
                else:
                    check_square(x, y + multiplier, only_empty = True)
                        
                check_square(x + multiplier, y + multiplier, True)
                check_square(x - multiplier, y + multiplier, True)
                
                if self.black:
                    en_passants = game.en_passants_w
                else:
                    en_passants = game.en_passants_b
                    
                en_passants = [flip(elem) for elem in en_passants]
                
                tuple = (x - multiplier, y + multiplier)
                found_passant = element_in_list(tuple, en_passants)
                if found_passant:
                    add_move(element_in_list(tuple, en_passants, ret = True))
                    
                tuple = (x + multiplier, y + multiplier)
                found_passant = element_in_list(tuple, en_passants)
                if found_passant:
                    add_move(element_in_list(tuple, en_passants, ret = True))
                      
            case 'knight':
                
                possible_moves = KNIGHT_MOVES
                            
            case "bishop":
                
                possible_moves = BISHOP_MOVES
            
            case 'queen':
                
                possible_moves = ROOK_MOVES[:-1] + BISHOP_MOVES
            
            case _:
                
                possible_moves = ROOK_MOVES
              
        if not self.type == 'pawn':  
            check_inc = possible_moves[-1]
            real_move = possible_moves[:-1]
            
            for move in real_move:
                m = move
                if check_inc:
                    check_increment(m[0], m[1])
                else:
                    check_square(x + m[0], y + m[1])
                    
        legal_moves = []
        for move in moves:
            if not check_move(test_rows, (x, y), flip(move), flipped = False)[1 if self.black else 0]:
                if type(self.get(tuple = move)) is not int:
                    if self.get(tuple = move).type != 'king':
                        legal_moves.append(move)
                else:
                    legal_moves.append(move)
            
        return legal_moves
    
    def string(self):
        if self.type != 'knight' and self.type not in 'lrookrrook':
            return f"{self.type[0]}{'b' if self.black else 'w'} "
        else:
            if self.type == 'knight':
                return f"n{'b' if self.black else 'w'} "   
            else:
                return f"r{'b' if self.black else 'w'} "
            
    def __str__(self) -> str:
        return f"{self.type}: {'black' if self.black else 'white'}"
    
def proportion(*args) -> list:
    return [a * SPACE_SIZE for a in (args[0] if len(args) == 1 else args)]
    
def element_in_list(element, list, ret = False) -> list | bool:
    list = [a for a in list if a[0] == element[0] and a[1] == element[1]]
    if ret:
        return list[0]
    else:
        return len(list) != 0
    
Chess()