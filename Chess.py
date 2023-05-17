import tkinter as tk
import Utils
import Check
import sv_ttk
import os
from tkinter import ttk
from CTkColorPicker import AskColor
from colour import Color
from PIL import Image, ImageTk
from math import floor
from ctypes import windll

windll.shcore.SetProcessDpiAwareness(1)

SPACE_SIZE = None #To be set after the window is created, as a fraction of the screen height
                  #So that the game is always proportioned to the screen
BASE_TIME = 1200
INCREMENT = 500
DEBUG = False

proportion = Utils._proportion
element_in_list = Utils._element_in_list
flip_list = Utils._flip_list
flip_num = Utils._flip_num
def colors() -> Utils._Color_Scheme:
    return Utils._get_scheme()
func = Utils._func

class Chess:  
    def __init__(self) -> None:
        self.turn               = 'white'
        self.playing            = False
        self.paused             = False
        self.flipped            = False
        self.promo_menu_showing = False
        self.settings_showing   = False
        self.flip_enabled       = True
        self.mouse_out          = False
        self.can_click          = True
        self.white_passants     = []
        self.black_passants     = []
        self.available_moves    = []
        self.move_counter       = 0
        self.options            = None
        self.rows               = [[[0] * 8] * 8]
        self.selected_position  = (0, 0)
        self.past_ids           = {}
        self.images             = {}
        
        self.root               = tk.Tk()
        
        Utils.SPACE_SIZE = int(self.root.winfo_screenheight() / 10)
        global SPACE_SIZE
        SPACE_SIZE = Utils.SPACE_SIZE
        
        pack = lambda widget, p_side = tk.LEFT, pad_x = 0, expand = False, fill = tk.NONE, pad_y = 0: widget.pack(side = p_side, padx = pad_x, expand = expand, fill = fill, pady = pad_y)
        
        draw = lambda: self.lose_game(method = '\nAgreement')
        self.font = font = ('Default', int(SPACE_SIZE / 9))
        big_font = ('Default', int(SPACE_SIZE / 9) + 6)
        
        def start():
            btn.destroy()
            canvas.delete('rect')
            lbl.destroy()
            self.start_game()

        self.root.overrideredirect(True)
        self.root.geometry(f'{SPACE_SIZE*8 + 40}x{int(SPACE_SIZE*9)}+50+50')
        
        canvas           = tk.Canvas(self.root, bg = colors().canvas_bg, width = SPACE_SIZE * 8, height = SPACE_SIZE * 8)
        timers_frame     = ttk.Frame(self.root, width = SPACE_SIZE * 8)
        bar_frame        = ttk.Frame(self.root, width = SPACE_SIZE * 8)
        white_lbl        = ttk.Label(timers_frame, text = 'W: \tPoints: ', font = big_font)
        black_lbl        = ttk.Label(timers_frame, text = 'B: \tPoints: \t', font = big_font)
        app_label        = ttk.Label(bar_frame, text = 'Chess', font = ('Typewriter', 20, 'italic'), background = colors().window_bg)
        options_btn      = ttk.Button(bar_frame, text = '⚙', style = 'Accent.TButton', command = self.show_settings, width = 3)
        draw_btn         = ttk.Button(bar_frame, text = 'Draw', style = 'Accent.TButton', state = 'disabled', command = draw, width = 8)
        close_btn        = ttk.Button(bar_frame, text = 'X', style = 'Accent.TButton', command = self.root.destroy, width = 3)
        
        self.white_label = white_lbl
        self.black_label = black_lbl
        self.app_label   = app_label
        self.draw_btn    = draw_btn
        self.canvas      = canvas
        self.bar_frame   = bar_frame
        self.options_btn = options_btn
        
        lbl = ttk.Label(canvas, text = 'Chess', font = ('Segoe UI', int(SPACE_SIZE / 9) + 15))
        self.round_rectangle(SPACE_SIZE * 2, SPACE_SIZE * 2, SPACE_SIZE * 6, SPACE_SIZE * 6, fill = colors().window_bg, outline = '', tag = 'rect')
        btn = ttk.Button(canvas, text = 'Start Game', style = 'Huge.Accent.TButton', command = start)
        
        lbl.place(relx = 0.5, rely = 0.4, anchor = tk.CENTER)
        btn.place(relx = 0.5, rely = 0.6, anchor = tk.CENTER)
        
        from tkinter import BOTTOM, TOP, RIGHT, LEFT, BOTH, Y
        
        pack(timers_frame, BOTTOM, expand = True, fill = BOTH)
        pack(bar_frame, TOP, expand = True, fill = BOTH)
        pack(white_lbl)
        pack(black_lbl, RIGHT)
        pack(close_btn, RIGHT, 10, fill = Y, pad_y = 15)
        pack(options_btn, RIGHT, 10, fill = Y, pad_y = 15)
        pack(draw_btn, RIGHT, 10, fill = Y, pad_y = 15)
        pack(canvas, TOP)
        pack(app_label, LEFT, pad_x = 20)
        
        self.get            = lambda y = 0, x = 0, tuple = 'empty': Utils._get(self.rows, y, x, tuple)
        self.any_selected   = lambda: self.selected_position != 0
        self.update         = self.canvas.update
        self.delete         = self.canvas.delete
        self.is_piece       = lambda x = 0, y = 0, obj = 0: is_piece(self.rows, x, y, obj)
        self.is_empty       = lambda x = 0, y = 0, obj = 0: is_empty(self.rows, x, y, obj)
        
        self.root.title('Chess')
        self.root.resizable(False, False)
        self.root.configure(bg = colors().window_bg, padx = 20)
        
        self.init_theme()
        
        self.reset_images()
        
        for row in range(0, 8):
            for column in range(0, 8):
                if (column + row * 8 + row) % 2 == 0:
                    (x, y) = proportion(column, row)
                    self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill = colors().canvas_fg, outline = '', tag = 'fg')
            
        self.canvas.tag_raise('piece')
        canvas.tag_raise('rect')
        
        #These two from: https://stackoverflow.com/questions/23836000/can-i-change-the-title-bar-in-tkinter
        def get_pos(event):
            window_x = self.root.winfo_x()
            window_y = self.root.winfo_y()
            click_x = event.x_root
            click_y = event.y_root

            self.relative_x = window_x - click_x
            self.relative_y = window_y - click_y
        
        def move_window(event):
            if self.options is not None:
                self.options.destroy()
            self.root.geometry(f'+{event.x_root + self.relative_x}+{event.y_root + self.relative_y}')
            
        #Code taken from https://stackoverflow.com/questions/30786337/tkinter-windows-how-to-view-window-in-windows-task-bar-which-has-no-title-bar
        #Necessary for better taskbar, full of windows jargon and complicated stuff I don't understand
        def set_appwindow(root):
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            hwnd = windll.user32.GetParent(root.winfo_id())
            style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
            style = style & ~WS_EX_TOOLWINDOW
            style = style | WS_EX_APPWINDOW
            windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
            root.withdraw()
            root.after(10, root.deiconify)
            
        self.root.bind('<Motion>',      self.motion)
        self.canvas.bind('<Button-1>',    func(self.click))
        self.bar_frame.bind('<B1-Motion>',  move_window)
        self.bar_frame.bind('<Button-1>',   get_pos)

        self.root.after(10, set_appwindow, self.root)
        self.root.mainloop()
    
    #https://stackoverflow.com/questions/44099594/how-to-make-a-tkinter-canvas-rectangle-with-rounded-corners
    def round_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
    
        points = [x1+radius, y1,
                x1+radius, y1,
                x2-radius, y1,
                x2-radius, y1,
                x2, y1,
                x2, y1+radius,
                x2, y1+radius,
                x2, y2-radius,
                x2, y2-radius,
                x2, y2,
                x2-radius, y2,
                x2-radius, y2,
                x1+radius, y2,
                x1+radius, y2,
                x1, y2,
                x1, y2-radius,
                x1, y2-radius,
                x1, y1+radius,
                x1, y1+radius,
                x1, y1]

        return self.canvas.create_polygon(points, **kwargs, smooth=True)
    
    def init_theme(self):
        def check_text(test):
            if (test[0].get().isdigit() or test[0].get() == '') and not len(test[0].get()) > 6:
                test[1] = test[0].get()
            else:
                test[0].set(test[1])
        
        self.root.configure(bg = colors().window_bg)
        style = ttk.Style()
        sv_ttk.use_dark_theme()
        style.theme_use('sun-valley-dark')
        
        self.time_string, self.inc_string = self.input_strings = [[tk.StringVar(), '1200'], [tk.StringVar(), '500']]
        self.time_string[0].trace('w', func(check_text, self.time_string))
        self.inc_string[0] .trace('w', func(check_text, self.inc_string))
        
        style.configure('Switch.TCheckbutton', font = self.font)
        style.configure('TCheckbutton', font = self.font)
        style.configure('Accent.TButton', font = self.font)
        style.configure('Huge.Accent.TButton', font = ('Segoe UI', int(SPACE_SIZE / 9) + 10))
        style.configure('TFrame', background = colors().window_bg)
        style.configure('TLabel', font = self.font)
        style.configure('Switch.TCheckbutton.Label', font = self.font)
        m = colors().widget_bg
        style.map('TCombobox', selectbackground = [('hover', m), ('focus', m), ('active', m), ('pressed', m), ('!focus', m)])
        m = colors().text_fg
        style.map('TCombobox', selectforeground = [('hover', m), ('focus', m), ('active', m), ('pressed', m), ('!focus', m)])
        
    def show_settings(self):
        
        if self.settings_showing:
            self.options.destroy()
            return
        
        self.settings_showing = True
        
        def switch_theme_color():
            Utils._dark = not Utils._dark
            self.root.configure(bg = colors().window_bg)
            style = ttk.Style()
            if Utils._dark:
                dark_toggle.configure(text = 'Light Mode')
                sv_ttk.use_dark_theme()
                style.theme_use('sun-valley-dark')
            else:
                dark_toggle.configure(text = 'Dark Mode')
                sv_ttk.use_light_theme()
                style.theme_use('sun-valley-light')
            
            self.app_label.configure(background = colors().window_bg)
            style.configure('TCheckbutton', font = self.font)
            style.configure('Accent.TButton', font = self.font)
            style.configure('Huge.Accent.TButton', font = ('Segoe UI', int(SPACE_SIZE / 9) + 10))
            self.canvas.itemconfig('rect', fill = colors().window_bg)
            m = colors().widget_bg
            style.map('TCombobox', selectbackground = [('hover', m), ('focus', m), ('active', m), ('pressed', m), ('!focus', m)])
            m = colors().text_fg
            style.map('TCombobox', selectforeground = [('hover', m), ('focus', m), ('active', m), ('pressed', m), ('!focus', m)])
            time_label.configure(font = self.font)
            inc_label.configure(font = self.font)
            theme_lbl.configure(font = self.font)
            self.options.configure(background = colors().widget_bg)

        def set_theme():
            Utils._set_theme(drop_down.get())
            self.reset_images()
            self.canvas.focus()
        
        def toggle_flip():
            if self.flipped:
                self.canvas.delete('last')
                self.flip()
            self.flip_enabled = flip_var.get()
        
        def show_credits():
            import webbrowser
            webbrowser.open("credits.txt")
        
        def destroy():
            border.destroy()
            self.settings_showing = False
            
        def get_color(bg_col = False):
            
            border.withdraw()
            self.options.withdraw()
            col = ColorPicker(initial_color = colors().canvas_bg if bg_col else colors().canvas_fg)
            col.set_changing(bg_col, self)
            col = col.get()
            if Utils._dark:
                if bg_col:
                    Utils._dark_c.canvas_bg = col
                else:
                    Utils._dark_c.canvas_fg = col
            else:
                if bg_col:
                    Utils._light_c.canvas_bg = col
                else:
                    Utils._light_c.canvas_fg = col
            
            update_colors()
            border.deiconify()
            self.options.deiconify()
            
        def update_colors():
            self.canvas.configure(bg = colors().canvas_bg)
            self.canvas.itemconfig('fg', fill = colors().canvas_fg)
            self.canvas.update()
            
        def reset_colors():
            Utils._reset_colors()
            update_colors()
        
        font = ('Default', int(SPACE_SIZE / 10))
        flip_var = tk.BooleanVar()
        
        col = Color(Utils._dark_c.widget_bg)
        col.set_luminance(1 - col.get_luminance())
        border = tk.Toplevel(self.root, background = col)
        border.withdraw()
        border.resizable(False, False)
        border.overrideredirect(True)
        
        self.options = tk.Toplevel(self.root, background = colors().widget_bg)
        self.options.resizable(False, False)
        self.options.overrideredirect(True)
        self.options.bind('<Destroy>', func(destroy))
        self.options.update_idletasks()
        
        r, btn = self.root, self.options_btn
        
        winwidth = int(self.options.winfo_width() / 2)
        width, height = btn.winfo_width(), btn.winfo_height()
        x, y = btn.winfo_x(), btn.winfo_y()
        rootx, rooty = r.winfo_x(), r.winfo_y()
        final_x, final_y = x + rootx - winwidth - width, y + rooty + height
        self.options.geometry(f'+{final_x}+{final_y + 5}')
        
        notebook = ttk.Notebook(self.options)
        
        state = 'disabled' if self.playing else 'normal'
        
        theme_options   = ttk.Frame      (notebook, padding = 10)
        
        dark_toggle     = ttk.Checkbutton(theme_options, text = 'Light Mode', style = 'Switch.TCheckbutton', command = switch_theme_color)
        theme_lbl       = ttk.Label      (theme_options, text = 'Icon Type: ', font = font)
        drop_down       = ttk.Combobox   (theme_options, values = os.listdir('resources/themes/'), state = 'readonly', font = font)
        
        game_options    = ttk.Frame      (notebook, padding = 10)
        
        time_label      = ttk.Label      (game_options, text = 'Time:     ', font = font)
        inc_label       = ttk.Label      (game_options, text = 'Increment:', font = font)
        inc_input       = ttk.Entry      (game_options, textvariable = self.inc_string[0], state = state)
        time_input      = ttk.Entry      (game_options, textvariable = self.time_string[0], state = state)
        f_toggle        = ttk.Checkbutton(game_options, text = 'Flipping', variable = flip_var, command = toggle_flip)
        credits         = ttk.Button     (game_options, text = 'Credits', style = 'Accent.TButton', command = show_credits)
        
        dark_pick       = ttk.Button     (theme_options, text = 'Dark', style = 'Accent.TButton', command = func(get_color, True))
        light_pick      = ttk.Button     (theme_options, text = 'Light', style = 'Accent.TButton', command = func(get_color))
        reset_color     = ttk.Button     (theme_options, text = 'Reset Colors', style = 'Accent.TButton', command = reset_colors)
        
        drop_down.bind("<<ComboboxSelected>>", func(set_theme))
        drop_down.set('cburnett')
        flip_var.set(self.flip_enabled)
        time_input.insert(0, str(BASE_TIME))
        inc_input.insert(0, str(INCREMENT))
        
        switch_theme_color()
        switch_theme_color()
        
        self.increment_input = inc_input
        self.time_input      = time_input
        
        ttk.Label(self.options, text = 'Settings', font = self.font).pack(pady = 10)
        dark_toggle.grid(column = 0, row = 0, columnspan = 2)
        theme_lbl.grid(column = 0, row = 1, pady = 10)
        drop_down.grid(column = 1, row = 1, pady = 10)
        ttk.Label(theme_options, text = 'Pick Square Colors: ', font = self.font).grid(pady = 10, column = 0, row = 2)
        reset_color.grid(column = 1, row = 2)
        dark_pick.grid(column = 0, row = 3, pady = 10)
        light_pick.grid(column = 1, row = 3, pady = 10)
        
        time_label.grid(column = 0, row = 0, padx = 10)
        inc_label.grid(column = 0, row = 1, pady = 10)
        time_input.grid(column = 1, row = 0, pady = 10)
        inc_input.grid(column = 1, row = 1)
        f_toggle.grid(column = 0, row = 2, pady = 10, columnspan = 2)
        credits.grid(column = 0, row = 3, columnspan = 2)

        notebook.add(game_options, text = 'Game Options')
        notebook.add(theme_options, text = 'Theme Options')
        
        notebook.pack(padx = 10, pady = 10, expand = True, fill = tk.BOTH)
        
        self.options.update_idletasks()
        border.geometry(f'{self.options.winfo_width() + 10}x{self.options.winfo_height() + 10}+{final_x - 5}+{final_y}')
        border.deiconify()
        self.options.lift()
        
    def reset_images(self):
        
        def img(file_name, pre = f'themes/{Utils._theme}', size = (SPACE_SIZE, SPACE_SIZE)):
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
        
        for row in self.rows:
            for square in row:
                if self.is_piece(obj = square):
                    square.set_image()

    def start_game(self):
        
        if self.input_strings[0][1].strip() == '' or self.input_strings[1][1].strip() == '':
            return
            
        self.base = int(self.input_strings[0][1])
        self.increment = int(self.input_strings[1][1])
        
        self.draw_btn.configure(state = 'normal')
        
        self.delete('on-start')
        
        self.timer                  = [self.base, self.base]
        self.black_king             = (4, 0)
        self.white_king             = (4, 7)
        self.playing                = True
        self.timer_started          = False
        self.turn                   = 'white'
        self.available_moves        = []
        
        piece_names = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
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
        self.draw_btn.configure(state = 'disabled')
        
        if not self.playing:
            return
        self.playing = False
        
        self.round_rectangle(SPACE_SIZE*2, SPACE_SIZE*2, SPACE_SIZE*6, SPACE_SIZE*6, fill = colors().window_bg, tag = 'rect')
        
        if winner != 'Draw':
            text = f'{winner} Won\nBy {method}'
            symbol  ='♚' if winner == 'black' else '♔'
        else:
            text = f'{winner} by {method}'
            symbol = '♔-♚'
            
        def restart():
            btn.destroy()
        
        self.canvas.create_text(proportion(4, 3), text = text, font = ('Default', int(SPACE_SIZE / 3)), fill = 'white', tag = ('title', 'on-start'), justify = tk.CENTER)
        self.canvas.create_text(proportion(4, 5), text = symbol, font = ('Default', int(SPACE_SIZE / 2)), fill = 'white', tag = ('title', 'on-start'), justify = tk.CENTER)
        btn = ttk.Button(self.canvas, style = 'Huge.Accent.TButton', text = 'Restart', command = restart)
        btn.place(relx = 0.5, rely = 0.5, anchor = tk.CENTER)
    
    def click(self):
        if self.options is not None:
            self.options.destroy()
        
        if not self.can_click:
            return
        
        self.delete('on-click')
         
        mouse_position = self.mouse_position
        
        if self.any_selected() and element_in_list(mouse_position, self.available_moves):
            self.move_to(mouse_position)
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
                
        if is_piece(obj = clicked_square):
            self.move_counter = 0
            self.delete(clicked_square.sprite)
            
        num = Utils._flip_num
        
        if selected_square.type == 'king':
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
                
        elif selected_square.type == 'pawn':
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
        self.switch_turn()
        
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
        if self.is_piece(obj = clicked_square):
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
        
        def select(type):
            self.can_click = True
            self.delete(self.get(tuple = position).sprite, 'pro')
            self.assign_element(position)
            self.assign_element(position, Piece(position, self, black, type))
            self.promo_menu_showing = False
            if self.flip_enabled:
                self.flip()
        
        self.canvas.tag_bind(queen  , '<Button-1>', func(select, 'queen'))
        self.canvas.tag_bind(rook   , '<Button-1>', func(select, 'rook'))
        self.canvas.tag_bind(bishop , '<Button-1>', func(select, 'bishop'))
        self.canvas.tag_bind(knight , '<Button-1>', func(select, 'knight'))
        
        self.can_click = False
                
    def motion(self, event):
        self.delete('hover')
        mouse_x = floor(event.x / SPACE_SIZE)
        mouse_y = floor(event.y / SPACE_SIZE)
            
        self.mouse_position = (mouse_x, mouse_y)
            
        if len(self.available_moves) != 0:
            if element_in_list(self.mouse_position, self.available_moves):
                piece = self.is_piece(*self.mouse_position)
                file_name = f"highlight-{'t' if piece else 'c'}"
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
        
        white_check, black_check = check = Check.test_move(self.rows, flipped = self.flipped)
        
        if check != [False, False]:
            self.create_img(self.white_king if white_check else self.black_king, self.images['check'], ('check', 'on-start'))
                
        white_moveable, black_moveable = [False, False]
                                
        for row in rows:
            for square in row:
                if self.is_empty(obj = square):
                    continue
                if square.black:
                    if len(square.get_moves((row.index(square), rows.index(row)))) > 0:
                        white_moveable = True
                        break
             
        for row in rows:
            for square in row:
                if self.is_empty(obj = square):
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
                if not is_piece(obj = square):
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
                if self.is_empty(obj = square):
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
            if self.is_piece(*move):
                string = 'move-take'
            self.create_img(move[:2], self.images[string], ('moves', 'on-click', 'on-start'), False)
            self.canvas.tag_raise('moves')
            
    def flip(self):
        
        if self.promo_menu_showing:
            return
        
        self.available_moves = []
        
        self.canvas.itemconfig('piece', state = 'hidden')
        
        for row in self.rows:
            for square in row:
                if not self.is_empty(obj = square):
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
        self.sprite = self.game.create_img(position, self.game.images[self.type][self.black])
            
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
                if is_piece(obj = piece):
                    if piece.black != self.black:
                        add_move(testing_x, testing_y)
                    break
                     
                add_move(testing_x, testing_y)
                testing_x += x_inc
                testing_y += y_inc
        
        def test_square(x, y, only_piece = False, only_empty = False) -> bool:
                    square = straight_get(y, x)
                    is_valid = lambda obj: is_piece(rows = 0, obj = obj) or is_empty(rows = 0, obj = obj)
                    if is_valid(square) and (type(square) is int or square.black != self.black):
                        if only_piece and not only_empty:
                            if is_piece(obj = square):
                                add_move(x, y)
                                return True
                        elif only_empty and not only_piece:
                            if is_empty(obj = square):
                                add_move(x, y)
                                return True
                        else:
                            add_move(x, y)
                            return True
                    return False
        
        def add_move(*move):
            moves.append(flip_list(move))
        
        _test = lambda *n_pos: Check.test_move(straight_rows, pos, n_pos, 'white' if not self.black else 'black', False)
        move_test = lambda *n_pos: not _test(*n_pos)[int(self.black)]
        
        match self.type:
            
            case 'king':
                
                possible_moves = Utils._moves_dict['king']
                
                empty = lambda y, x: is_empty(straight_rows, x, y)
                
                right_moved, left_moved = [True, True]
                
                left_rook = straight_get(y, 7)
                if is_piece(obj = left_rook):
                    if not left_rook.moved:
                        left_moved = False
                        
                right_rook = straight_get(y, 0)
                if is_piece(obj = right_rook):
                    if not right_rook.moved:
                        right_moved = False
                        
                if not self.moved:
                    
                    if not left_moved:
                        if empty(y, x + 1) and empty(y, x + 2):
                            if move_test(*pos) and move_test(x + 1, y):
                                add_move(x + 2, y)
                                
                    if not right_moved:
                        if empty(y, x - 1) and empty(y, x - 2) and empty(y, x - 3):
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
                        if is_empty(straight_rows, *elem):
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
    
    def set_image(self):
        self.game.canvas.itemconfig(self.sprite, image = self.game.images[self.type][self.black])
    
    def piece_id(self):
        if self.type == 'knight':
            return f"n{'b' if self.black else 'w'}{int(self.moved)} "   
        else:
            return f"{self.type[0]}{'b' if self.black else 'w'}{int(self.moved)} "

def is_empty(rows = 0, x = 1, y = 1, obj = 1):
    if obj == 1:
        return Utils._get(rows, y, x) == 0
    else:
        return obj == 0

def is_piece(rows = 0, x = 1, y = 1, obj = 1):
    if obj == 1:
        return type(Utils._get(rows, y, x)) is Piece
    else:
        return type(obj) is Piece

class ColorPicker(AskColor):
    def set_changing(self, bg: bool, game):
        self.bg = bg
        self.game = game
        
    def on_mouse_drag(self, event):
        super().on_mouse_drag(event)
        c = Color()
        c.set_rgb([col / 255 for col in self.rgb_color])
        c = c.get_hex()
        if self.bg:
            self.game.canvas.configure(background = c)
        else:
            self.game.canvas.itemconfig('fg', fill = c)

game = Chess()