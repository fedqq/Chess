from copy import copy

def check_check(rows, white_king, black_king) -> str:
    white = check_king(rows, white_king, 'w')
    print(white)
    black = check_king(rows, black_king, 'b')
    print(black)
    print('')
    if white:
        return 'white'
    if black:
        return 'black'
    else:
        return 'none'
            
def check_king(rows, king, c):
    black = (c == 'b')
    multi = 1
    if black:
        multi = -1
    
    x = king[0] + (1 * multi)
    y = king[1] + (1 * multi)
    square = get(y, x, rows)
    while square != 'NA':
        if type(square) is not int:
            if square.black != black:
                if square.type == 'queen' or square.type == 'bishop':
                    return True
            else:
                break
            
        y += 1
        x += 1
        square = get(y, x, rows)
        
    x = king[0] - (1 * multi)
    y = king[1] + 1 * multi
    square = get(y, x, rows)
    while square != 'NA':
        if type(square) is not int:
            if square.black != black:
                if square.type == 'queen' or square.type == 'bishop':
                    return True
            else:
                break
            
        y += 1
        x -= 1
        square = get(y, x, rows)
        
        
    first = True
    x = king[0] - (1 * multi)
    y = king[1] - (1 * multi)
    square = copy(get(y, x, rows))
    while square != 'NA':
        if type(square) is not int:
            if square.black != black:
                if square.type == 'queen' or square.type == 'bishop' or (first and square.type == 'pawn'):
                    return True
            else:
                break
            
        y -= 1
        x -= 1
        square = copy(get(y, x, rows))
        first = False
    
    first = True
    x = king[0] + 1 * multi
    y = king[1] - (1 * multi)
    square = get(y, x, rows)
    while square != 'NA':
        if type(square) is not int:
            if square.black != black:
                if square.type == 'queen' or square.type == 'bishop' or (first and square.type == 'pawn'):
                    return True
            else:
                break
            
        y -= 1
        x += 1
        square = get(y, x, rows)
        first = False
        
    return False
    
def get(y, x, rows):
    if y not in range(0, 8) or x not in range(0, 8):
        return 'NA'
    else:
        return rows[y][x]