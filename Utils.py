SPACE_SIZE = 0
_flipped = False
_theme = 'cburnett'
_dark = True

def _set_theme(theme = 'cburnett'):
    global _theme
    _theme = theme
    
class _Color_Scheme:
    def __init__(self, *args) -> None:
        self.main_bg, self.background, self.front_color, self.widget_color, self.text_fill = args
        
_dark_c = _Color_Scheme('#1C1C1C', '#686868', '#E6F4F4', '#2A2A2A', '#FAFAFA')
_light_c = _Color_Scheme('#FAFAFA', '#686868', '#E6F4F4', '#F9F9F9', '#1C1C1C')
    
def _get_scheme():
    if _dark:
        return _dark_c
    else:
        return _light_c

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
    
#Returns a lambda that calls function arg with parameters in args, and ignores the event argument provided by the tkinter handler
def _func(function, *args):
    return lambda *a: function(*args)

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
    
