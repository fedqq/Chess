from copy import copy

def check_mate(*args):
    pass

def check_check(rows, white_king, black_king) -> str:
    white = check_king(rows, white_king, 'w')
    black = check_king(rows, black_king, 'b')
    if white:
        return 'white'
    if black:
        return 'black'
    else:
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
    
    x = king[0] + 1
    y = king[1] + 1
    square = get(y, x, rows)
    while square != 'NA':
        if type(square) is not int:
            if square.black != black:
                if square.type == 'queen' or square.type == 'bishop':
                    return True
            else:
                break
            
        x += 1
        y += 1
        square = get(y, x, rows)
        
    x = king[0] + 1
    y = king[1] - 1
    square = get(y, x, rows)
    while square != 'NA':
        if type(square) is not int:
            if square.black != black:
                if square.type == 'queen' or square.type == 'bishop':
                    return True
            else:
                break
            
        x += 1
        y -= 1
        square = get(y, x, rows)
        
    x = king[0] - 1
    y = king[1] - 1
    square = copy(get(y, x, rows))
    while square != 'NA':
        if type(square) is not int:
            if square.black != black:
                if square.type == 'queen' or square.type == 'bishop':
                    return True
            else:
                break
            
        y -= 1
        x -= 1
        square = copy(get(y, x, rows))
    
    x = king[0] + 1
    y = king[1] - 1
    square = get(y, x, rows)
    while square != 'NA':
        if type(square) is not int:
            if square.black != black:
                if square.type == 'queen' or square.type == 'bishop':
                    return True
            else:
                break
            
        x -= 1
        y += 1
        square = get(y, x, rows)
        
    return False
    
def get(y, x, rows):
    if y not in range(0, 8) or x not in range(0, 8):
        return 'NA'
    else:
        return rows[y][x]