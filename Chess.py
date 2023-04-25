import tkinter as tk
from tkinter import ttk
import Utils
from Check import test_move
from PIL import Image, ImageTk
from math import floor
import sv_ttk
from ctypes import windll

windll.shcore.SetProcessDpiAwareness(1)

SPACE_SIZE = None #To be set after the window is created, as a fraction of the screen height
BASE_TIME = 1200
INCREMENT = 500
DEBUG = True

proportion = Utils._proportion
element_in_list = Utils._element_in_list
flip_list = Utils._flip_list
flip_num = Utils._flip_num

class Chess:  
    def __init__(self) -> None:
        global SPACE_SIZE
        
        self.turn               = 'white'
        self.playing            = False
        self.paused             = False
        self.flipped            = False
        self.promo_menu_showing = False
        self.flip_enabled       = True
        self.mouse_out          = True
        self.can_click          = True
        self.white_passants     = []
        self.black_passants     = []
        self.available_moves    = []
        self.move_counter       = 0
        self.rows               = [[[0] * 8] * 8]
        self.selected_position  = (0, 0)
        self.past_ids           = {}
        self.images             = {}
        
        self.root               = tk.Tk()
        
        Utils.SPACE_SIZE = int(self.root.winfo_screenheight() / 10)
        SPACE_SIZE = Utils.SPACE_SIZE
        
        pack = lambda widget, p_side = tk.LEFT, pad_x = 0, expand = False, fill = tk.NONE: widget.pack(side = p_side, padx = pad_x, expand = expand, fill = fill)
        
        time_string, inc_string = self.input_strings = [[tk.StringVar(), '1200'], [tk.StringVar(), '500']]
        time_string[0] .trace('w', lambda *args: check_text(time_string))
        inc_string[0]  .trace('w', lambda *args: check_text(inc_string))
        b_var = tk.BooleanVar()
        
        def check_text(test):
            if (test[0].get().isdigit() or test[0].get() == '') and not len(test[0].get()) > 6:
                test[1] = test[0].get()
            else:
                test[0].set(test[1])
        
        def toggle_flip():
            self.flip_enabled = b_var.get()
            
        draw = lambda: self.lose_game(method = '\nAgreement')
        font = ('Segoe UI', 22)
        
        canvas = self.canvas          = tk.Canvas(self.root, bg = Utils._Variables.BACKGROUND.value, width = SPACE_SIZE * 8, height = SPACE_SIZE * 8)
        settings_frame = self.options = ttk.Frame(self.root, width = SPACE_SIZE * 8)
        label_frame = self.labels     = ttk.Frame(self.root, width = SPACE_SIZE * 8)
        
        white_lbl = self.white_label     = ttk.Label  (label_frame, text = 'W: \tPoints: ', font = font)
        black_lbl = self.black_label     = ttk.Label  (label_frame, text = 'B: \tPoints: \t', font = font)
        draw_btn = self.draw_btn         = ttk.Button (settings_frame, command = draw, text = 'Draw', style = 'Accent.TButton', state = 'disabled')
        inc_input = self.increment_input = ttk.Entry  (settings_frame, textvariable = inc_string[0], width = 7)
        time_input = self.time_input     = ttk.Entry  (settings_frame, textvariable = time_string[0], width = 7)
        time_label = ttk.Label          (settings_frame, text = 'Time: ')
        inc_label = ttk.Label           (settings_frame, text = ' + ')
        f_toggle = ttk.Checkbutton      (settings_frame, text = 'Flipping', command = toggle_flip, variable = b_var)
        
        time_input.insert(0, str(BASE_TIME))
        inc_input.insert(0, str(INCREMENT))
        b_var.set(True)
        
        RIGHT = tk.RIGHT
        TOP = tk.TOP
        
        pack(white_lbl)
        pack(black_lbl, RIGHT)
        pack(time_label)
        pack(time_input)
        pack(inc_label)
        pack(inc_input)
        pack(f_toggle, RIGHT, 10)
        pack(draw_btn, RIGHT, 20)
        pack(label_frame, TOP, expand = True, fill = tk.BOTH)
        pack(canvas, TOP)
        pack(settings_frame, TOP, expand = True, fill = tk.BOTH)
        
        sv_ttk.set_theme('dark')
        style = ttk.Style(self.root)
        style.theme_use('sun-valley-dark')
        style.configure('TCheckbutton', font = ("Segoe UI", 15))
        style.configure('TEntry',       font = ("Segoe UI", 15))
        style.configure('TLabel',       font = ("Segoe UI", 15))
        
        self.get            = lambda y = 0, x = 0, tuple = 'empty': Utils._get(self.rows, y, x, tuple)
        self.any_selected   = lambda: self.selected_position != 0
        self.update         = self.canvas.update
        self.delete         = self.canvas.delete
        
        self.root.title('Chess')
        self.root.resizable(False, False)
        self.root.configure(bg = Utils._Variables.MAIN_BG.value, padx = 20)
        
        def img(file_name, pre = 'pieces', size = (SPACE_SIZE, SPACE_SIZE)):
            image = Image.open(f'resources/{pre}/{file_name}.png')
            return ImageTk.PhotoImage(image.resize(size, Image.LANCZOS))
        
        def add_piece(*args):
            piece = args[-1]
            args = args[:-1]
            if piece:
                for name in args:
                    self.images[name] = {False: img(name + '-w'), True: img(name + '-b')}
            else:
                for name in args:
                    self.images[name] = img(name, 'other')
        
        add_piece('pawn', 'rook', 'bishop', 'knight', 'queen', 'king', True)
        add_piece('move-take', 'move-circle', 'highlight-c', 'highlight-t', 'check', 'last', 'highlight', False)
        
        self.images['promote']  = img('promote', 'other', (SPACE_SIZE * 4, SPACE_SIZE))
        self.images['end-menu'] = img('promote', 'other', (SPACE_SIZE * 8, SPACE_SIZE * 8))
        
        for row in range(0, 8):
            for column in range(0, 8):
                if (column + row * 8 + row) % 2 == 0:
                    (x, y) = proportion(column, row)
                    self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill = Utils._Variables.FRONT_COLOR.value, outline = '')
            
        self.canvas.tag_raise('piece')
        
        def change(b):
            self.mouse_out = b
            
        self.canvas.bind('<Enter>',     lambda *args: change(False))
        self.canvas.bind('<Leave>',     lambda *args: change(True))
        self.root.bind('<Motion>',    self.motion)
        self.root.bind('<Button-1>',  self.click)

        self.root.mainloop()

    def start_game(self):
        
        if self.input_strings[0][1].strip() == '' or self.input_strings[1][1].strip() == '':
            return
            
        self.base = int(self.input_strings[0][1])
        self.increment = int(self.input_strings[1][1])
            
        self.increment_input.configure(state = 'disabled')
        self.time_input.configure(state = 'disabled')
        self.draw_btn.configure(state = 'normal')
        
        self.delete('on-start')
        
        self.timer                  = [self.base, self.base]
        self.black_king             = (4, 0)
        self.white_king             = (4, 7)
        self.playing                = True
        self.timer_started          = False
        self.turn                   = 'white'
        self.available_moves        = []
        
        piece_names = ['lrook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rrook']
        self.rows = [
                     [Piece((index, 0), self, True, piece_names[index]) for index in range(8)], 
                     [Piece((index, 1), self, True) for index in range(8)], 
                     [0] * 8, 
                     [0] * 8, 
                     [0] * 8, 
                     [0] * 8, 
                     [Piece((index, 6), self, False) for index in range(8)],
                     [Piece((index, 7), self, False, piece_names[index]) for index in range(8)]
                    ]
        
        self.past_ids = {self.get_position_id(): 1}
   
    def lose_game(self, winner = 'Draw', method = 'Checkmate'):
        self.time_input.configure(state = 'normal')
        self.increment_input.configure(state = 'normal')
        self.draw_btn.configure(state = 'disabled')
        
        if not self.playing:
            return
        self.playing = False
        
        self.create_img((0, 0), self.images['end-menu'], 'title', False)
        
        if winner != 'Draw':
            text = f'{winner} Won\nBy {method}'
            symbol  ='♚' if winner == 'black' else '♔'
        else:
            text = f'{winner} by {method}'
            symbol = '♔-♚'
        
        self.canvas.create_text(proportion(4, 3), text = text, font = ('Segoe UI', 54), fill = 'white', tag = ('title', 'on-start'), justify = tk.CENTER)
        self.canvas.create_text(proportion(4, 5), text = symbol, font = ('Segoe UI', 100), fill = 'white', tag = ('title', 'on-start'), justify = tk.CENTER)
        
    def click(self, event):
        if not self.playing:
            if not self.mouse_out:
                self.start_game()
            return
        
        if not self.can_click:
            return
        
        if self.mouse_out:
            self.deselect()
            return
        
        self.delete('on-click')
         
        mouse_position = self.mouse_position
        
        if self.any_selected():
            if element_in_list(mouse_position, self.available_moves):
                self.move_to(mouse_position)
            else:
                self.select_position(mouse_position)
        else:
            self.select_position(mouse_position)
            
    def move_to(self, new_pos):
        select_position = self.selected_position 
        assign = self.assign_element
        canvas = self.canvas
        get = self.get
        
        selected_square: Piece = self.get(tuple = select_position)
        square_sprite = selected_square.sprite
        clicked_square: Piece = get(tuple = new_pos)
                
        if type(clicked_square) is Piece:
            self.move_counter = 0
            self.delete(clicked_square.sprite)
            
        num = Utils._flip_num
        
        match selected_square.type:
            case 'king':
                if selected_square.black:
                    self.black_king = new_pos
                else:
                    self.white_king = new_pos
                
                row = num(0 if selected_square.black else 7)
                    
                multi = -1 if self.flipped else 1
                
                if new_pos[0] - select_position[0] == (2 * multi):
                    
                    canvas.move(get(row, num(7)).sprite, SPACE_SIZE * -2 * multi, 0)
                    assign((num(5), row), get(row, num(7)))
                    assign((num(7), row))
                    
                elif new_pos[0] - select_position[0] == (-2 * multi):
                    
                    canvas.move(get(row, num(0)).sprite, SPACE_SIZE * 3 * multi, 0)
                    assign((num(3), row), get(row, num(0)))
                    assign((num(0), row))
                        
            case 'pawn':
                
                self.move_counter = 0
                
                if abs(select_position[1] - new_pos[1]) == 2:
                    object = (select_position[0], int((select_position[1] + new_pos[1]) / 2), new_pos[0], new_pos[1])
                    if selected_square.black:
                        self.black_passants.append(object)
                    else:
                        self.white_passants.append(object)
                        
                if new_pos[1] == (num(7) if selected_square.black else num(0)):
                    self.show_promote_menu(new_pos, selected_square.black)
                    
        move = element_in_list(new_pos, self.available_moves, ret = True)
            
        if len(move) > 3 and selected_square.type == 'pawn':
            self.delete(self.get(move[3], move[2]).sprite)
            assign((move[2], move[3]))
        
        assign(new_pos, selected_square)
        assign(self.selected_position)
        selected_square.move()
        
        self.delete('last')
        
        canvas.moveto(square_sprite, y = new_pos[1] * SPACE_SIZE, x = new_pos[0] * SPACE_SIZE)
        self.last_move = (select_position, new_pos)
        
        if not self.flipped:
            self.test_draw()
        
        if self.flip_enabled:
            self.update()
            self.pause_timer()
            self.can_click = False
            self.flip()
            if not self.flipped:
                self.test_draw()
        else:
            self.create_img(self.last_move[0], self.images['last'], ('last', 'on-start'))
            self.create_img(self.last_move[1], self.images['last'], ('last', 'on-start'))
            
        self.update()
        
        self.deselect()
        self.test_check()
                    
    def select_position(self, pos):
        if pos == self.selected_position:
            self.deselect()
            return
        black = (self.turn == 'black')
        clicked_square = self.get(tuple = pos)
        if type(clicked_square) is Piece:
            if clicked_square.black == black or DEBUG:
                
                moves = clicked_square.get_moves(pos)
                clicked_square.select(pos)
                self.draw_moves(moves)
                
                if not self.timer_started:
                    self.timer_started = True
                    self.tick_timer()
                self.selected_position = pos 
            else:
                self.deselect()
                
    def deselect(self):
        
        self.delete('on-click')
        self.selected_position = 0
        self.available_moves = []
        
    def create_img(self, position, image, tag = ('piece', 'on-start'), raise_pieces = True):
            ret = self.canvas.create_image(proportion(position), image = image, anchor = tk.NW, tag = tag)
            if raise_pieces:
                self.canvas.tag_raise('piece')
            return ret
        
    def show_promote_menu(self, position, black = False):
        self.promo_menu_showing = True
        pos = (2, 3.5)
        self.create_img(pos, self.images['promote'], tag = 'pro')
        
        queen       = self.create_img(        pos         , self.images['queen' ][black], tag = 'pro')
        rook        = self.create_img((pos[0] + 1, pos[1]), self.images[ 'rook' ][black], tag = 'pro')
        bishop      = self.create_img((pos[0] + 2, pos[1]), self.images['bishop'][black], tag = 'pro')
        knight      = self.create_img((pos[0] + 3, pos[1]), self.images['knight'][black], tag = 'pro')
        
        self.canvas.tag_bind(queen  , '<Button-1>', lambda e: select('queen' ))
        self.canvas.tag_bind(rook   , '<Button-1>', lambda e: select( 'rook' ))
        self.canvas.tag_bind(bishop , '<Button-1>', lambda e: select('bishop'))
        self.canvas.tag_bind(knight , '<Button-1>', lambda e: select('knight'))
        
        self.can_click = False
        
        def select(type):
            self.can_click = True
            self.delete(self.get(tuple = position).sprite, 'pro')
            self.assign_element(position)
            self.assign_element(position, Piece(position, self, black, type))
            self.promo_menu_showing = False
            if self.flip_enabled:
                self.flip()
                
    def motion(self, event):
            self.delete('hover')
            mouse_x = floor(event.x / SPACE_SIZE)
            mouse_y = floor(event.y / SPACE_SIZE)
                
            self.mouse_position = (mouse_x, mouse_y)
                
            if len(self.available_moves) != 0:
                if element_in_list(self.mouse_position, self.available_moves):
                    is_piece = type(self.get(tuple = self.mouse_position)) is Piece
                    file_name = f"highlight-{'t' if is_piece else 'c'}"
                    self.create_img(self.mouse_position, self.images[file_name], ('hover', 'on-start', 'on-click'))
           
    def switch_turn(self):
        
        if self.turn == 'white':
            self.turn = 'black'
            self.timer[1] += INCREMENT
            if not DEBUG:
                self.black_passants.clear()
        else:
            self.turn = 'white'
            self.timer[0] += INCREMENT
            if not DEBUG:
                self.white_passants.clear()

    def assign_element(self, place, element = 0):
        self.rows[place[1]][place[0]] = element
        
    def pause_timer(self):
        self.paused = True
        
    def tick_timer(self):
        if self.paused:
            self.root.after(1000, self.tick_timer)
            
        if self.turn == 'white' or DEBUG:
            self.timer[0] -= 1
        else:
            self.timer[1] -= 1
            
        if self.timer[0] == 0:
            self.lose_game('Black', '\nTime Limit')
            return
        if self.timer[1] == 0:
            self.lose_game('White', '\nTime Limit')
            return
        
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
        self.root.after(1000, self.tick_timer)
        
    def test_draw(self):
        
        self.move_counter += 1
        code = self.get_position_id()
                
        if code in self.past_ids:
            self.past_ids[code] += 1
        else:
            self.past_ids[code] = 1
            
        if self.past_ids[code] == 3:
            self.lose_game(method = '\nThreefold Repetition')
            
        if self.move_counter == 100:
            self.lose_game(method = '\nFifty Move Rule')
        
    def test_check(self) -> tuple:
        self.delete('check')
        rows = self.rows
        
        white_check, black_check = check = test_move(self.rows, flipped = self.flipped)
        
        if check != [False, False]:
            self.create_img(self.white_king if white_check else self.black_king, self.images['check'], ('check', 'on-start'))
                
        white_moveable, black_moveable = [False, False]
                                
        for row in rows:
            for square in row:
                if type(square) is int:
                    continue
                if square.black:
                    if len(square.get_moves((row.index(square), rows.index(row)))) > 0:
                        white_moveable = True
                        break
             
        for row in rows:
            for square in row:
                if type(square) is int:
                    continue
                if not square.black:
                    if len(square.get_moves((row.index(square), rows.index(row)))) > 0:
                        black_moveable = True
                        break
                
        if not white_moveable:
            if black_check:
                self.lose_game('White')
                return
            else:
                self.lose_game(method = 'Stalemate')
        
        if not black_moveable:
            if white_check: 
                self.lose_game('Black')
                return
            else:
                self.lose_game()
    
    def get_position_id(self):
        
        string = ''
        
        for row in self.rows:
            for square in row:
                if type(square) is int:
                    string += '0'
                else:
                    string += square.piece_id()
                    
        if len(self.black_passants) < 1:
            string += '0'
        
        for pos in self.black_passants:
            string += f'{pos}'
            
        if len(self.white_passants) < 1:
            string += '0'
        
        for pos in self.white_passants:
            string += f'{pos}'
            
        string += f'{self.turn[0]}'
        
        return string

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
            
    def draw_moves(self, moves):
        self.available_moves = moves
        for move in moves:
            string = 'move-circle'
            if type(self.get(move[1], move[0])) is Piece:
                string = 'move-take'
            self.create_img(move[:2], self.images[string], ('moves', 'on-click', 'on-start'))
            
    def flip(self):
        
        if self.promo_menu_showing:
            return
        
        self.available_moves = []
        
        self.canvas.itemconfig('piece', state = 'hidden')
        
        for row in self.rows:
            for square in row:
                if not type(square) is int:
                    self.canvas.moveto(square.sprite, x = (flip_num(row.index(square), True)) * SPACE_SIZE, y = (7-self.rows.index(row)) * SPACE_SIZE)
                    self.canvas.itemconfigure(square.sprite, state = 'normal')
                    self.update()
                    
        self.paused = False
        self.flipped = not self.flipped
        Utils._flipped = self.flipped
        self.rows = [row[::-1] for row in self.rows][::-1]
            
        self.white_passants = flip_list(self.white_passants, True)
        self.black_passants = flip_list(self.black_passants, True)
         
        self.white_king = flip_list(self.white_king, True)
        self.black_king = flip_list(self.black_king, True)
        
        self.last_move = flip_list(self.last_move, True)
        
        self.create_img(self.last_move[0], self.images['last'], ('last', 'on-start'))
        self.create_img(self.last_move[1], self.images['last'], ('last', 'on-start'))
        
        self.can_click = True
        
        self.update()
        
        self.test_check()
        self.update()
    
class Piece:
    def __init__(self, position = '', game: Chess = None, black = False, piece_type = 'pawn'):
        self.type = piece_type
        self.game = game
        self.black = black
        self.moved = False
        self.start_position = (position[0], position[1])
        self.get = lambda y = 0, x = 0, tuple = 'empty': Utils._get(game.rows, y, x, tuple)
        self.sprite = self.game.create_img(position, self.game.images['rook' if 'rook' in self.type else self.type][self.black])
            
    def select(self, position):
        self.game.create_img(position, self.game.images['highlight'], ('highlight', 'on-start', 'on-click'))
        
    def move(self):
        self.moved = True
        
    def get_moves(self, position) -> list:
        
        moves = []
        
        multiplier = 1 if self.black else -1
        
        pos = flip_list(position)
        x, y = pos
        
        game = self.game
        
        straight_rows = game.rows
        if game.flipped:
            straight_rows = [row[::-1] for row in straight_rows][::-1]
        
        straight_get = lambda y, x: Utils._get(straight_rows, y, x)
        
        def check_increment(x_inc, y_inc):
            testing_x = x + x_inc
            testing_y = y + y_inc
                        
            while straight_get(testing_y, testing_x) != 'NA':
                            
                piece: Piece = straight_get(testing_y, testing_x)
                if type(piece) is Piece:
                    if piece.black != self.black:
                        add_move(testing_x, testing_y)
                    break
                     
                add_move(testing_x, testing_y)
                testing_x += x_inc
                testing_y += y_inc
        
        def test_square(x, y, only_piece = False, only_empty = False) -> bool:
                    square = straight_get(y, x)
                    if type(square) is not str and (type(square) is int or square.black != self.black):
                        if only_piece and not only_empty:
                            if type(square) is Piece:
                                add_move(x, y)
                                return True
                        elif only_empty and not only_piece:
                            if type(square) is not Piece:
                                add_move(x, y)
                                return True
                        else:
                            add_move(x, y)
                            return True
                    return False
        
        def add_move(*move):
            moves.append(flip_list(move))
            
        move_test = lambda *n_pos: test_move(straight_rows, pos, n_pos, 'white' if not self.black else 'black', self.game.flipped)[int(self.black)] == False
        
        match self.type:
            
            case 'king':
                
                possible_moves = Utils._moves_dict['king']
                
                right_moved, left_moved = [True, True]
                
                left_rook = straight_get(y, 7)
                if type(left_rook) is not int:
                    if not left_rook.moved:
                        left_moved = False
                        
                right_rook = straight_get(y, 0)
                if type(right_rook) is not int:
                    if not right_rook.moved:
                        right_moved = False
                        
                if not self.moved:
                    
                    if not left_moved:
                        if straight_get(y, x + 1) == 0 and straight_get(y, x + 2) == 0:
                            if move_test(*pos) and move_test(x + 1, y):
                                add_move(x + 2, y)
                                
                    if not right_moved:
                        if straight_get(y, x - 1) == 0 and straight_get(y, x - 2) == 0 and straight_get(y, x - 3) == 0:
                            if move_test(*pos) and move_test(x - 1, y) and move_test(x - 2, y):
                                add_move(x - 2, y)
                                
            
            case 'pawn':
                if not self.moved:
                    if test_square(x, y + multiplier, only_empty = True) and move_test(x, y + multiplier):
                        test_square(x, y + 2 * multiplier, only_empty = True)
                else:
                    test_square(x, y + multiplier, only_empty = True)
                        
                test_square(x + multiplier, y + multiplier, True)
                test_square(x - multiplier, y + multiplier, True)
                
                en_passants = game.white_passants if self.black else game.black_passants
                    
                en_passants = flip_list(en_passants)
                
                def pass_test(*tup):
                    found_passant = element_in_list(tup, en_passants)
                    if found_passant:
                        elem = element_in_list(tup, en_passants, ret = True)
                        if type(straight_get(elem[1], elem[0])) is int:
                            add_move(*tuple(elem))
                
                pass_test(x - multiplier, y + multiplier)
                pass_test(x + multiplier, y + multiplier)
                      
            case _:
                piece_type = 'rook' if 'rook' in self.type else self.type
                possible_moves = Utils._moves_dict[piece_type]
              
        if not self.type == 'pawn':  
            check_inc = possible_moves[-1]
            possible_moves = possible_moves[:-1]
            
            for move in possible_moves:
                m = move
                if check_inc:
                    check_increment(m[0], m[1])
                else:
                    test_square(x + m[0], y + m[1])
                    
        legal_moves = []
        for move in moves:
            if move_test(*flip_list(move)):
                if type(self.get(tuple = move)) is not int:
                    if self.get(tuple = move).type != 'king':
                        legal_moves.append(move)
                else:
                    legal_moves.append(move)
            
        return legal_moves
    
    def piece_id(self):
        if self.type != 'knight' and self.type not in 'lrookrrook':
            return f"{self.type[0]}{'b' if self.black else 'w'} "
        else:
            if self.type == 'knight':
                return f"n{'b' if self.black else 'w'}{int(self.moved)} "   
            else:
                return f"r{'b' if self.black else 'w'}{int(self.moved)} "
    
Chess()