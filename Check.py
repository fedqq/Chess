def check_move(original_rows, start_move = 0, end_move = 0, test = 'all', flipped = False):
    rows = [[TestPiece(square) for square in row] for row in original_rows]
    if not start_move == end_move:
        rows[end_move[1]][end_move[0]] = rows[start_move[1]][start_move[0]] 
        rows[start_move[1]][start_move[0]] = 0
    
    ret = [False, False]
    
    if test != 'black':
        for row_index, row in enumerate(rows):
            for square_index, square in enumerate(row):
                if type(square) is not int and square.type != 'int':
                    if square.type == 'king' and not square.black:
                        ret[0] = check_king(rows, (square_index, row_index), black = False, flipped = flipped)
                        break
                        
    if test != 'white':
        for row_index, row in enumerate(rows):
            for square_index, square in enumerate(row):
                if type(square) is not int and square.type != 'int':
                    if square.type == 'king' and square.black:
                        ret[1] = check_king(rows, (square_index, row_index), black = True, flipped  = flipped)
                        break
         
    return ret

def check_king(rows, king, black, flipped):
    
    def check_moves(x_inc, y_inc, types):
        
        x = king[0] + x_inc
        y = king[1] + y_inc
        square = get(rows, y, x)
        while square != 'NA':
            
            if type(square) is not int and square.type != 'int':
                if square.black != black:
                    if square.type in types:
                        return True
                    else:
                        break
                else:
                    break
                
            x += x_inc
            y += y_inc
            square = get(rows, y, x)
    
    qb = ('queen', 'bishop')
    qr = ('queen', 'rrook', 'lrook', 'rook')
    checks = [(1, -1, qb), (-1, 1, qb), (1, 1, qb), (-1, -1, qb), (-1, 0, qr), (1, 0, qr), (0, 1, qr), (0, -1, qr)]
    for check in checks:
        if check_moves(check[0], check[1], check[2]):
            return True
    
    a = black
    multi = 1
    if flipped:
        a = not a
        multi = 1
    if a:
        left = get(rows, king[1] + (1*multi), king[0] - 1)
        right = get(rows, king[1] + (1*multi), king[0] + 1)
        
        if type(left) is not int and type(left) is not str and left.type != 'int':
            if left.type == 'pawn' and left.black != black:
                return True
            
        if type(right) is not int and type(right) is not str and right.type != 'int':
            if right.type == 'pawn' and right.black != black:
                return True
            
    else:
        left = get(rows, king[1] - (1*multi), king[0] - 1)
        right = get(rows, king[1] - (1*multi), king[0] + 1)
        
        if type(left) is not int and type(left) is not str and left.type != 'int':
            if left.type == 'pawn' and left.black != black:
                return True
            
        if type(right) is not int and type(right) is not str and right.type != 'int':
            if right.type == 'pawn' and right.black != black:
                return True    
    
    for move in ((2, 1), (1, 2), (-2, 1), (2, -1), (-2, -1), (-1, 2), (-1, -2), (1, -2)):
        absolute_move = (move[0] + king[0], move[1] + king[1])
        square = get(rows, absolute_move[1], absolute_move[0])
        if type(square) is not int and square != 'NA':
            if square.type == 'knight':
                if square.black != black:
                    return True
        
    return False
    
def get(rows, yp = 0, xp = 0, tuple = 'empty'):
    if tuple != 'empty':
        x = tuple[0]
        y = tuple[1]
    else:
        x = xp
        y = yp
        
    if x in range(0, 8) and y in range(0, 8):
        return rows[y][x]
    
    return 'NA'
    
class TestPiece:
    def __init__(self, base):
        if type(base) is not int:
            
            self.type = base.type
            self.black = base.black
            self.position = (base.start_position[0], base.start_position[1])
            self.selected = False 
        else:
            self.type = 'int'