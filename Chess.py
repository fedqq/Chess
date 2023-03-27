from tkinter import *
from copy import copy
from Check import check_check, check_mate

SPACE_SIZE = 120
OA = 5
MC = '#43e86f'
BBG = '#B48767'
SBG = '#EBD6B7'
HC = '#646F40'

class Chess:
    def __init__(self) -> None:
        self.window = Tk()
        self.window.title('Chess')
        self.window.resizable(False, False)
        self.window.configure(bg = "black")
        self.selected = (False, (0, 0))
        self.selected_square = (0, 0)
        self.any_selected = False
        
        self.images = {'pawn':          {False : PhotoImage(file = 'resources/pawn-w.png'), 
                                         True : PhotoImage(file = 'resources/pawn-b.png')}, 
                       'rook':          {False : PhotoImage(file = 'resources/rook-w.png'), 
                                         True : PhotoImage(file = 'resources/rook-b.png')}, 
                       'knight':        {False : PhotoImage(file = 'resources/knight-w.png'), 
                                         True : PhotoImage(file = 'resources/knight-b.png')}, 
                       'bishop':        {False : PhotoImage(file = 'resources/bishop-w.png'), 
                                         True : PhotoImage(file = 'resources/bishop-b.png')}, 
                       'queen':         {False : PhotoImage(file = 'resources/queen-w.png'), 
                                         True : PhotoImage(file = 'resources/queen-b.png')}, 
                       
                       'move-take':         PhotoImage(file = 'resources/move-take.png'), 
                       'move-circle':       PhotoImage(file = 'resources/move-circle.png'), 
                       'highlight':         PhotoImage(file = 'resources/highlight.png'), 
                       'highlight-circle':  PhotoImage(file = 'resources/highlight-circle.png'), 
                       'highlight-take':    PhotoImage(file = 'resources/highlight-take.png')
                       }
        
        self.canvas = Canvas(self.window, bg = BBG, width = SPACE_SIZE * 8, height = SPACE_SIZE * 8, bd = 0, relief = RAISED)

        self.rows = [[0 for _ in range(0, 8)] for _ in range(0, 8)]
        
        i = 0
        for row in range(len(self.rows)):
            for square in range(len(self.rows[row])):
                if ((square + (row * 8)) + i) % 2 == 0:
                    x = square * SPACE_SIZE
                    y = row * SPACE_SIZE
                    self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill = SBG, outline = '', tag = 'bg')
            i += 1
            
        self.canvas.tag_lower('bg')

        self.canvas.pack()
        
        self.game_started = False
        self.moves = []
        self.turn = 'white'   
        self.playing = False
            
        self.window.bind('<Motion>', self.motion)
        self.window.bind('<Button-1>', self.click)
        self.window.bind('<Up>', self.asdf)
        
        self.start_game()
        
        self.window.mainloop()
        
    def start_game(self):
        self.playing = True
        self.turn = 'white'
        self.moves = []
        
        self.rows = [
                     [Piece((1, 1), self, True, 'rook'), Piece((2, 1), self, True, 'knight'), Piece((3, 1), self, True, 'bishop'), Piece((4, 1), self, True, 'queen'), Piece((5, 1), self, True, 'king'), Piece((6, 1), self, True, 'bishop'), Piece((7, 1), self, True, 'knight'), Piece((8, 1), self, True, 'rook')], 
                     [Piece((1, 2), self, True), Piece((2, 2), self, True), Piece((3, 2), self, True), Piece((4, 2), self, True), Piece((5, 2), self, True), Piece((6, 2), self, True), Piece((7, 2), self, True), Piece((8, 2), self, True)], 
                     [0 for _ in range(0, 8)],
                     [0 for _ in range(0, 8)], 
                     [0 for _ in range(0, 8)], 
                     [0 for _ in range(0, 8)], 
                     [Piece((1, 7), self), Piece((2, 7), self), Piece((3, 7), self), Piece((4, 7), self), Piece((5, 7), self), Piece((6, 7), self), Piece((7, 7), self), Piece((8, 7), self)], 
                     [Piece((1, 8), self, False, 'rook'), Piece((2, 8), self, False, 'knight'), Piece((3, 8), self, False, 'bishop'), Piece((4, 8), self, False, 'queen'), Piece((5, 8), self, False, 'King'), Piece((6, 8), self, False, 'bishop'), Piece((7, 8), self, False, 'knight'), Piece((8, 8), self, False, 'rook')], 
                    ]
        
        self.black_king = (4, 0)
        self.white_king = (4, 7)
        
    def asdf(self, e):
        print(check_check(self.rows, self.white_king, self.black_king))
        
    def motion(self, event):
            self.canvas.delete('hover')
            x = event.x - event.x % SPACE_SIZE
            y = event.y - event.y % SPACE_SIZE
            
            self.x = int(x / SPACE_SIZE)
            self.y = int(y / SPACE_SIZE)
            
            if len(self.moves) != 0:
                if (self.x, self.y) in self.moves:
                    if type(self.rows[self.y][self.x]) is Piece:
                        self.canvas.create_image(x, y, image = self.images['highlight-take'], anchor = NW, tag = 'hover')
                    else:
                        self.canvas.create_image(x, y, image = self.images['highlight-circle'], anchor = NW, tag = 'hover')
                    self.canvas.tag_raise('piece')
        
    def switch_turn(self):
        if self.turn == 'white':
            self.turn = 'black'
        else:
            self.turn = 'white'
        
    def click(self, event):
        
        self.canvas.delete('hover')
        
        if not self.playing:
            return
        self.canvas.delete('moves', 'check')
        click_square: Piece = self.rows[self.y][self.x]
        click_coords = (self.x, self.y)
        
        if self.any_selected:
            select_square: Piece = self.rows[self.selected_square[1]][self.selected_square[0]]
            
            moves = select_square.get_moves(self.selected_square)
            if click_coords in moves:
                
                object = select_square.obj
                if type(self.rows[click_coords[1]][click_coords[0]]) is Piece:
                    self.canvas.delete(self.rows[click_coords[1]][click_coords[0]].obj)
                self.rows[click_coords[1]][click_coords[0]] = copy(select_square)
                self.rows[self.selected_square[1]][self.selected_square[0]] = 0
                self.switch_turn()
                
                self.canvas.moveto(object, y = self.y * SPACE_SIZE, x = self.x * SPACE_SIZE)
                
                if select_square.type == 'king':
                    if select_square.black:
                        self.black_king = click_coords
                    else:
                        self.white_king = click_coords
                
                select_square.unclick()
                self.moves = []
                self.any_selected = False
            else:
                if click_square == select_square:
                    self.canvas.delete('moves')
                    select_square.unclick() 
                    self.moves = []
                    self.any_selected = False
                    return
                self.canvas.delete('moves')
                select_square.unclick()
                black = (self.turn == 'black')
                if type(click_square) is Piece:
                    if click_square.black == black or (1 == 1):
                        self.any_selected = True
                        click_square.click(click_coords)
                        self.draw_moves(click_square.get_moves(click_coords))
                        self.selected_square = click_coords
                    else:
                        self.moves = []
                        self.any_selected = False
                
        else:
            select_square: Piece = self.rows[self.selected_square[1]][self.selected_square[0]]
            if type(click_square) is not int:
                black = (self.turn == 'black')
                if click_square.black == black or (1 == 1):
                    click_square.click(click_coords)
                    
                    self.selected_square = click_coords
                    self.any_selected = True
                    self.draw_moves(click_square.get_moves(click_coords))
        self.check_check()
                        
    def check_check(self, rows = '') -> tuple:
        if rows == '':
            rows = self.rows
        
        check = check_check(rows, self.white_king, self.black_king)
        
        if check:
            mate = check_mate(rows, self.white_king, 'w')
        else:
            mate = False
        
        return (check, False)
            
        
    def draw_moves(self, moves):
        self.moves = moves
        for move in moves:
            x = move[0] * SPACE_SIZE
            y = move[1] * SPACE_SIZE
            string = 'move-circle'
            if type(self.rows[move[1]][move[0]]) is Piece:
                string = 'move-take'
            self.canvas.create_image(x, y, image = self.images[string], anchor = NW, tag = 'moves')
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
    
    def get(self, y, x):
        if y not in range(0, 8):
            return 1
        elif x not in range(0, 8):
            return 1
        else:
            return self.game.rows[y][x]
    
class Piece:
    def __init__(self, coordinates = '', game: Chess = None, black = False, piece_type = 'pawn') -> None:
        self.type = piece_type
        self.game = game
        self.black = black
        
        self.coordinates = (coordinates[0] - 1, coordinates[1] - 1)
        self.selected = False
        
        x = coordinates[0] * SPACE_SIZE - SPACE_SIZE
        y = coordinates[1] * SPACE_SIZE - SPACE_SIZE
        
        self.color = ''
        if self.type == 'pawn':
            self.color = 'green'
        else:
            self.color = 'blue'
        
        match self.type:
            
            case 'pawn' | 'rook' | 'knight' | 'bishop' | 'queen':
                self.obj = self.game.canvas.create_image(x, y, image = self.game.images[self.type][self.black], anchor = NW, tag = 'piece')
                
            case _:
                self.obj = self.game.canvas.create_rectangle(x + 10, y + 10, x + SPACE_SIZE - 10, y + SPACE_SIZE - 10, fill = self.color, tag = 'piece', outline = '')
            
    
    def click(self, coords):
        self.selected = True
        if self.type == 'king':
            self.game.canvas.itemconfigure(self.obj, fill = 'pink')
        else:
            x = coords[0] * SPACE_SIZE
            y = coords[1] * SPACE_SIZE
            self.game.canvas.create_image(x, y, image = self.game.images['highlight'], anchor = NW, tag = 'highlight')
            self.game.canvas.tag_raise('piece')
        
        
    def unclick(self):
        self.selected = False
        if self.type != 'king':
            self.game.canvas.delete('highlight')
        else:
            self.game.canvas.itemconfigure(self.obj, fill = self.color)
        
    def get_moves(self, coordinates):
        moves = []
        multiplier = -1
        if self.black:
            multiplier = 1
            
        current_x = coordinates[0]
        current_y = coordinates[1]
        
        match self.type:
            
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
                      
            case 'knight':
                
                for move in ((2, 1), (1, 2), (-2, 1), (2, -1), (-2, -1), (-1, 2), (-1, -2), (1, -2)):
                    piece = self.get(current_y + move[0], current_x + move[1])
                    if piece != 1:
                        if type(piece) is Piece:
                            if piece.black != self.black:
                                moves.append((current_x + move[1], current_y + move[0]))
                        else:
                            moves.append((current_x + move[1], current_y + move[0]))
                            
            case _:
                if self.type == 'rook' or self.type == 'queen':
                    x = copy(current_x) + 1
                    
                    while self.get(current_y, x) != 1:
                        
                        piece: Piece = self.get(current_y, x)
                        if type(piece) is Piece:
                            if piece.black != self.black:
                                moves.append((x, current_y))
                            break
                        
                        moves.append((x, current_y))
                        x += 1
                    
                    x = copy(current_x) -1
                    
                    while self.get(current_y, x) != 1:
                        
                        piece: Piece = self.get(current_y, x)
                        if type(piece) is Piece:
                            if piece.black != self.black:
                                moves.append((x, current_y))
                            break
                        
                        moves.append((x, current_y))
                        x -= 1
                        
                    y = copy(current_y) + 1
                    
                    while self.get(y, current_x) != 1:
                        
                        piece: Piece = self.get(y, current_x)
                        if type(piece) is Piece:
                            if piece.black != self.black:
                                moves.append((current_x, y))
                            break
                        
                        moves.append((current_x, y))
                        y += 1
                    
                    y = copy(current_y) - 1
                    
                    while self.get(y, current_x) != 1:
                        
                        piece: Piece = self.get(y, current_x)
                        if type(piece) is Piece:
                            if piece.black != self.black:
                                moves.append((current_x, y))
                            break
                        
                        moves.append((current_x, y))
                        y -= 1
                if self.type == 'bishop' or self.type == 'queen':
                    
                    x = copy(current_x) + 1
                    y = copy(current_y) + 1
                    
                    while self.get(y, x) != 1:
                        
                        piece: Piece = self.get(y, x)
                        if type(piece) is Piece:
                            if piece.black != self.black:
                                moves.append((x, y))
                            break
                        
                        moves.append((x, y))
                        x += 1
                        y += 1
                    
                    x = copy(current_x) + 1
                    y = copy(current_y) - 1
                    
                    while self.get(y, x) != 1:
                        
                        piece: Piece = self.get(y, x)
                        if type(piece) is Piece:
                            if piece.black != self.black:
                                moves.append((x, y))
                            break
                        
                        moves.append((x, y))
                        x += 1
                        y -= 1
                        
                    x = copy(current_x) - 1
                    y = copy(current_y) + 1
                    
                    while self.get(y, x) != 1:
                        
                        piece: Piece = self.get(y, x)
                        if type(piece) is Piece:
                            if piece.black != self.black:
                                moves.append((x, y))
                            break
                        
                        moves.append((x, y))
                        x -= 1
                        y += 1
                    
                    x = copy(current_x) - 1
                    y = copy(current_y) - 1
                    
                    while self.get(y, x) != 1:
                        
                        piece: Piece = self.get(y, x)
                        if type(piece) is Piece:
                            if piece.black != self.black:
                                moves.append((x, y))
                            break
                        
                        moves.append((x, y))
                        x -= 1
                        y -= 1
        
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
            test = check_check(test_rows, self.game.white_king, self.game.black_king)
            if test != string:
                legal_moves.append(move)
            
        return legal_moves
    
    def get(self, y, x):
        if y not in range(0, 8):
            return 1
        elif x not in range(0, 8):
            return 1
        else:
            return self.game.rows[y][x]
        
    def __str__(self) -> str:
        return f'{self.type}'
    
    def __unicode__(self):
        return f'{self.type}'
    def __repr__(self):
        return f'{self.type}'
    
    
game = Chess()