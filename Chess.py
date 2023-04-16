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

"testssyasdf"

class Chess:  
    def __init__(self) -> None:
        self.window = Tk()
        self.window.title('Chess')
        self.window.resizable(False, False)
        self.window.configure(bg = MAIN_BG)
        self.selected_position = (0, 0)
        self.any_selected = False
        
        self.get = lambda y = 0, x = 0, tuple = 'empty': get(self.rows, y, x, tuple)
        
        def img(file_name, pre = 'pieces', size = (SPACE_SIZE, SPACE_SIZE)):
            image = Image.open(f'resources/{pre}/{file_name}.png')
            resized = image.resize(size)
            return ImageTk.PhotoImage(resized)
        
        self.images = {'pawn':      {False: img('pawn-w'), 
                                     True : img('pawn-b')}, 
                       'rook':      {False: img('rook-w'), 
                                     True : img('rook-b')},
                       'knight':    {False: img('knight-w'), 
                                     True : img('knight-b')}, 
                       'bishop':    {False: img('bishop-w'), 
                                     True : img('bishop-b')}, 
                       'queen':     {False: img('queen-w'), 
                                     True : img('queen-b')}, 
                       'king':      {False: img('king-w'), 
                                     True : img('king-b')},
                       
                       'move-take':         img('move-take', 'other'), 
                       'promote':           img('promote', 'other', (SPACE_SIZE * 4, SPACE_SIZE)), 
                       'end-menu':          img('lost-menu', 'other', (SPACE_SIZE * 8, SPACE_SIZE * 8)), 
                       'move-circle':       img('move-circle', 'other'), 
                       'highlight':         img('highlight', 'other'), 
                       'highlight-c':       img('highlight-c', 'other'), 
                       'highlight-t':       img('highlight-t', 'other'), 
                       'check':             img('check'), 
                       'last-move':         img('last-move', 'other')
                       }
        
        self.turn               = 'white'
        self.playing            = False
        self.paused             = False
        self.flipped            = False
        self.promo_on           = False
        self.flip_on            = True
        self.game_started       = False
        self.out                = True
        self.can_click          = True
        self.white_moved        = [False, False, False]
        self.black_moved        = [False, False, False]
        self.en_passants_w      = []
        self.en_passants_b      = []
        self.moves              = []
        self.move_counter       = 0
            
        self.canvas = Canvas(self.window, bg = MAIN_BG, width = SPACE_SIZE * 8, height = SPACE_SIZE * 8, bd = 0, relief = FLAT)
        self.label = Label(self.window, text = 'White: \t\tBlack: \t\t', bg = MAIN_BG, font = ('times new roman', 27), fg = 'white')
        self.canvas.tag_lower('bg')
            
        def change(b):
            self.out = b
            
        self.canvas.bind('<Enter>',     lambda *args: change(False))
        self.canvas.bind('<Leave>',     lambda *args: change(True))
        self.window.bind('<Motion>',    self.motion)
        self.window.bind('<Button-1>',  self.click)
        self.window.bind('f',         lambda e: self.toggle_flip())
        
        self.input_strings = [[StringVar(), '1200'], [StringVar(), '500']]
        font = ('times new roman', 20)
        
        self.time_label = Label(self.window, text = 'Time: ', font = font, bg = MAIN_BG, fg = 'white')
        self.time_input = Entry(self.window, bg = MAIN_BG, fg = 'white', bd = 0, font = font, textvariable = self.input_strings[0][0], width = 7)
        self.time_input.insert(0, f'{BASE_TIME}')
        
        self.increment_label = Label(self.window, text = ' + ', font = font, bg = MAIN_BG, fg = 'white')
        self.increment_input = Entry(self.window, bg = MAIN_BG, fg = 'white', bd = 0, font = font, textvariable = self.input_strings[1][0], width = 7)
        self.increment_input.insert(0, f'{INCREMENT}')
        
        self.rows = [[0 for _ in range(0, 8)] for _ in range(0, 8)]
        
        self.game_positions = {}
        
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
        
        self.update = self.canvas.update
        
        self.window.mainloop()
        
    def create_image(self, position, image, tag = 'pro'):
            ret = self.canvas.create_image(proportion(position), image = image, anchor = NW, tag = tag)
            self.canvas.tag_raise('piece')
            return ret
        
    def show_promote_menu(self, position, black = False):
        self.promo_on = True
        pos = (2, 3.5)
        self.create_image(pos, self.images['promote'])
        
        queen       = self.create_image(pos,                  self.images['queen'  ][black])
        rook        = self.create_image((pos[0] + 1, pos[1]), self.images['rook'   ][black])
        bishop      = self.create_image((pos[0] + 2, pos[1]), self.images['bishop' ][black])
        knight      = self.create_image((pos[0] + 3, pos[1]), self.images['knight' ][black])
        
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
                self.flip(True)
        
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
        self.playing = False
        self.create_image((0, 0), self.images['end-menu'], 'title')
        if winner != 'Draw':
            text = f'{winner} Won\nBy {method}'
            symbol  ='♚' if winner == 'black' else '♔'
        else:
            text = f'{winner} by {method}'
            symbol = '♔-♚'
        
        self.canvas.create_text(proportion(4, 3), text = text, font = ('times new roman', 54), fill = 'white', tag = 'title', justify = CENTER)
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
                    
                    self.create_image(self.mouse_position, self.images[f"highlight-{'t' if test else 'c'}"], 'hover')
    
    def toggle_flip(self):
        self.flip_on = not self.flip_on
        print(self.flip_on)
              
    def switch_turn(self):
        
        if self.turn == 'white':
            self.turn = 'black'
            self.timer[1] += INCREMENT
            #self.en_passants_b.clear()
        else:
            self.turn = 'white'
            self.timer[0] += INCREMENT
            #self.en_passants_w.clear()
        
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
                            self.black_moved[0] = True
                            self.black_king = mouse_position
                        else:
                            self.white_moved[0] = True
                            self.white_king = mouse_position
                        
                        if selected_square.black:
                            row = num(0)
                        else:
                            row = num(7)
                            
                        multi = 1
                        if self.flipped:
                            multi = -1
                        
                        if mouse_position[0] - select_position[0] == (2 * multi):
                            
                            canvas.move(get(row, num(7)).sprite, SPACE_SIZE * (-2 * multi), 0)
                            assign((num(5), row), get(row, num(7)))
                            assign((num(7), row))
                            
                        elif mouse_position[0] - select_position[0] == (-2 * multi):
                            
                            canvas.move(get(row, num(0)).sprite, SPACE_SIZE * (3 * multi), 0)
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
                            
                move = element_in_list(mouse_position, self.moves, True)
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
                    if self.flipped:
                        self.window.after(500, self.flip, True)
                    else:
                        self.window.after(500, self.flip)
                        
                else:
                    self.create_image(self.last_move[0], self.images['last-move'], 'last')
                    self.create_image(self.last_move[1], self.images['last-move'], 'last')
                    
                self.update()
                
                self.moves = []
                self.any_selected = False
                select_position = ()
                self.test_check()
                
            else:
                if mouse_position == select_position:
                    self.moves = []
                    self.any_selected = False
                    select_position = ()
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
        self.label.configure(text = f'White: {white}\tBlack: {black}\t')
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
                self.lose_game(method = 'stalemate')
    
    def draw_moves(self, moves):
        self.moves = moves
        for move in moves:
            string = 'move-circle'
            if type(self.get(move[1], move[0])) is Piece:
                string = 'move-take'
            self.create_image(move[:2], self.images[string], 'moves')
            
    def flip(self, check_draw = False):
        
        if self.promo_on:
            return
        
        for row in self.rows:
            for square in row:
                if not type(square) is int:
                    self.canvas.moveto(square.sprite, x = (7 - row.index(square)) * SPACE_SIZE, y = (7-self.rows.index(row)) * SPACE_SIZE)
                    self.canvas.itemconfigure(square.sprite, state = 'normal')
                    for a in range(0,100000):
                        pass
                    self.canvas.update()
                    
        self.paused = False
        self.flipped = not self.flipped
        self.rows = [row[::-1] for row in self.rows][::-1]
            
        self.en_passants_w = [[7 - elem for elem in p] for p in self.en_passants_w]
        self.en_passants_b = [[7 - elem for elem in p] for p in self.en_passants_b]
         
        self.white_king = [7 - elem for elem in self.white_king]
        self.black_king = [7 - elem for elem in self.black_king]
        
        self.last_move = [[7 - elem for elem in p] for p in self.last_move]
        
        self.create_image(self.last_move[0], self.images['last-move'], 'last')
        self.create_image(self.last_move[1], self.images['last-move'], 'last')
        
        self.can_click = True
        
        self.update()
        
        self.test_check()
        self.update()
        
        if check_draw:
            self.test_draw()
    
class Piece:
    def __init__(self, position = '', game: Chess = None, black = False, piece_type = 'pawn'):
        self.type = piece_type
        self.game = game
        self.black = black
        self.moved = False
        self.start_position = (position[0], position[1])
        self.get = lambda y = 0, x = 0, tuple = 'empty': get(game.rows, y, x, tuple)
        self.sprite = self.game.create_image(position, self.game.images['rook' if 'rook' in self.type else self.type][self.black], 'piece')
            
    def select(self, position):
        self.game.create_image(position, self.game.images['highlight'], 'highlight')
        
    def move(self):
        self.moved = True
        
    def get_moves(self, position) -> list:
        moves = []
        if self.game.flipped:
            flip_mult = -1
        else:
            flip_mult = 1
        multiplier = -1 * flip_mult
        if self.black:
            multiplier = 1 * flip_mult
            
        x = position[0]
        y = position[1]
        
        game = self.game
        
        rows = game.rows
        
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
                    moved = game.black_moved
                    if self.game.flipped:
                        row = 7
                        multi = -1
                    else:
                        row = 0
                        multi = 1
                else:
                    
                    moved = game.white_moved
                    if self.game.flipped:
                        row = 0
                        multi = -1
                    else:
                        row = 7
                        multi = 1
                    
                print(moved)
                    
                g = lambda *args: self.get(args[0], args[1])
                check = lambda i, n_pos = pos: check_move(rows, pos, n_pos, 'b' if self.black else 'w', self.game.flipped)[i] == False
                
                def num(n):
                    if self.game.flipped:
                        return 7 - n
                    else:
                        return n
                
                if not moved[0]:
                    if not moved[2]:
                        if g(row, num(1)) == 0 and g(row, num(2)) == 0 and g(row, num(3)) == 0 and g(row, num(4)) != 0:
                            print(check(1) and check(1, (row, 1)) and check(1, (row, 2)) and check(1, (row, 3)))
                            if check(1) and check(1, (row, 1)) and check(1, (row, 2)) and check(1, (row, 3)):
                                moves.append((x - (2*multi), y))
                            
                    if not moved[1]:
                        if g(row, 5) == 0 and g(row, 6) == 0 and g(row, 7) != 0:
                            if check(0) and check(0, (row, 5)) and check(0, (row, 6)):
                                moves.append((x + (2*multi), y))
            
            case 'pawn':
                if not self.moved:
                    if check_square(x, y + 1 * multiplier, only_empty = True) and not check_move(rows, pos, (x, y + 1 * multiplier), flipped = self.game.flipped)[1 if self.black else 0]:
                        check_square(x, y + 2 * multiplier, only_empty = True)
                        
                else:
                    check_square(x, y + 1 * multiplier, only_empty = True)
                        
                check_square(x + 1 * multiplier, y + 1 * multiplier, True)
                check_square(x - 1 * multiplier, y + 1 * multiplier, True)
                
                if self.black:
                    en_passants = game.en_passants_w
                else:
                    en_passants = game.en_passants_b
                
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
            if not check_move(rows, (x, y), move, flipped = self.game.flipped)[1 if self.black else 0]:
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
    
def proportion(*args) -> list:
    return [a * SPACE_SIZE for a in (args[0] if len(args) == 1 else args)]
    
def element_in_list(element, list, ret = False) -> list | bool:
    list = [a for a in list if a[0] == element[0] and a[1] == element[1]]
    if ret:
        return list[0]
    else:
        return len(list) != 0
    
Chess()