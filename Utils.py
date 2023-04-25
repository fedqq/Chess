from enum import Enum
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import fitz
from PIL import Image, ImageTk
import os
import shutil

SPACE_SIZE = 0
_flipped = False

def _set_theme(theme):
    path = f'resources/themes/{theme}/'
    new_path = 'resources/themed-pieces/'
    shutil.rmtree(new_path)
    os.mkdir(new_path)
    make_image(f'{new_path}bishop-b.png', f'{path}bB.svg')
    make_image(f'{new_path}bishop-w.png', f'{path}wB.svg')
    make_image(f'{new_path}rook-b.png', f'{path}bR.svg')
    make_image(f'{new_path}rook-w.png', f'{path}wR.svg')
    make_image(f'{new_path}king-b.png', f'{path}bK.svg')
    make_image(f'{new_path}king-w.png', f'{path}wK.svg')
    make_image(f'{new_path}knight-b.png', f'{path}bN.svg')
    make_image(f'{new_path}knight-w.png', f'{path}wN.svg')
    make_image(f'{new_path}pawn-b.png', f'{path}bP.svg')
    make_image(f'{new_path}pawn-w.png', f'{path}wP.svg')
    make_image(f'{new_path}queen-b.png', f'{path}bQ.svg')
    make_image(f'{new_path}queen-w.png', f'{path}wQ.svg')
    
def make_image(name, og_file_name):
    drawing = svg2rlg(og_file_name)
    pdf = renderPDF.drawToString(drawing)

    doc = fitz.Document(stream=pdf)
    page = doc.load_page(0)
    '''page.set_mediabox(fitz.Rect(2, -3, 131, 126))'''
    pix = page.get_pixmap(alpha=True, dpi=300)
    pix.save(name)

class _Variables(Enum):
    MAIN_BG = '#1C1C1C'
    BACKGROUND = '#686868'
    FRONT_COLOR = '#E6F4F4'
    BASE_TIME = 1200
    INCREMENT = 500

#The last value determines whether the moves signify an incremental change with those values or an absolute move to those positions relative to the piece's position
_moves_dict = {'knight': ((2, 1), (1, 2), (-2, 1), (2, -1), (-2, -1), (-1, 2), (-1, -2), (1, -2), False), 
               'king': ((0, 1), (1, 0), (1, 1), (-1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1), False), 
               'rook': ((-1, 0), (1, 0), (0, -1), (0, 1), True), 
               'bishop': ((-1, -1), (1, -1), (-1, 1), (1, 1), True), 
               'queen': ((-1, -1), (1, -1), (-1, 1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1), True)}

class _TestPiece:
    def __init__(self, base):
        if type(base) is not int:
            
            self.type = base.type
            self.black = base.black
            self.position = (base.start_position[0], base.start_position[1])
            self.selected = False 
        else:
            self.type = 'int'
            
    def __str__(self) -> str:
        if self.type == 'int':
            return '0'
        return f"{self.type[:2]}: {'b' if self.black else 'w'}"

def _get(rows, yp = 0, xp = 0, tuple = 'empty'):
    if tuple != 'empty':
        x = tuple[0]
        y = tuple[1]
    else:
        x = xp
        y = yp
        
    if x in range(0, 8) and y in range(0, 8):
        return rows[y][x]
    
    return 'NA'

def _flip_list(_list, ignore_flipped = False):
    if len(_list) == 0:
        return _list
    
    if type(_list[0]) is list or type(_list[0]) is tuple:
        if ignore_flipped or _flipped:
            return [_flip_list(elem, ignore_flipped) for elem in _list]
        else:
            return _list
    else:
        if ignore_flipped or _flipped:
            return [7 - elem for elem in _list]
        else:
            return _list
    
def _flip_num(n, ignore_flipped = False):
    if ignore_flipped or _flipped:
        return 7 - n
    else:
        return n

def _proportion(*args) -> list:
    return [a * SPACE_SIZE for a in (args[0] if len(args) == 1 else args)]
    
def _element_in_list(element, list, ret = False) -> list | bool:
    list = [a for a in list if a[0] == element[0] and a[1] == element[1]]
    if ret:
        return list[0]
    else:
        return len(list) != 0
    
