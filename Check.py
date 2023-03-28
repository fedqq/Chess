from copy import copy

def check_mate(*args):
    pass

def check_check(rows, white_king, black_king, test = 'all') -> str:
    white = check_king(rows, white_king, 'w')
    if white:
        return 'white'
        
    black = check_king(rows, black_king, 'b')
    if black:
        return 'black'
        
    return 'none'
            
def check_king(rows, king, c):
        
    black = (c == 'b')
    
    if black:
        left = get(king[1] + 1, king[0] - 1, rows)
        right = get(king[1] + 1, king[0] + 1, rows)
        
        if type(left) is not int and type(left) is not str:
            if left.type == 'pawn' and not left.black:
                return True
            
        if type(right) is not int and type(right) is not str:
            if right.type == 'pawn' and not right.black:
                return True
            
    else:
        left = get(king[1] - 1, king[0] - 1, rows)
        right = get(king[1] - 1, king[0] + 1, rows)
        
        if type(left) is not int and type(left) is not str:
            if left.type == 'pawn' and left.black:
                return True
            
        if type(right) is not int and type(right) is not str:
            if right.type == 'pawn' and right.black:
                return True
            
    def check_moves(x_inc, y_inc, types):
        
        x = king[0] + x_inc
        y = king[1] + y_inc
        square = get(y, x, rows)
        while square != 'NA':
            
            if type(square) is not int:
                if square.black != black:
                    if square.type in types:
                        return True
                else:
                    break
                
            x += x_inc
            y += y_inc
            square = get(y, x, rows)
        
    tests = []
    if check_moves(1, -1, ('queen', 'bishop')):
        return True
    if check_moves(-1, 1, ('queen', 'bishop')):
        return True
    if check_moves(1, 1, ('queen', 'bishop')):
        return True
    if check_moves(-1, -1, ('queen', 'bishop')):
        return True
    
    if check_moves(-1, 0, ('queen, rook')):
        return True
    if check_moves(1, 0, ('queen, rook')):
        return True
    if check_moves(0, 1, ('queen, rook')):
        return True
    if check_moves(0, -1, ('queen, rook')):
        return True
    
    if True in tests:
        return True
        
    return False
    
def get(y, x, rows):
    if y not in range(0, 8) or x not in range(0, 8):
        return 'NA'
    else:
        return rows[y][x]