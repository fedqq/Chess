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
        
    qb = ('queen', 'bishop')
    qr = ('queen, rrook, lrook')
    checks = [(1, -1, qb), (-1, 1, qb), (1, 1, qb), (-1, -1, qb), (-1, 0, qr), (1, 0, qr), (0, 1, qr), (0, -1, qr)]
    for check in checks:
        if check_moves(check[0], check[1], check[2]):
            return True
    
    for move in ((2, 1), (1, 2), (-2, 1), (2, -1), (-2, -1), (-1, 2), (-1, -2), (1, -2)):
        absolute_move = (move[0] + king[0], move[1] + king[1])
        square = get(absolute_move[1], absolute_move[0], rows)
        if type(square) is not int and square != 'NA':
            if square.type == 'knight':
                if square.black != black:
                    return True
        
    return False
    
def get(y, x, rows):
    if y not in range(0, 8) or x not in range(0, 8):
        return 'NA'
    else:
        return rows[y][x]