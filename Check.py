class Testpiece:
    def __init__(self, base):
        if type(base) is not int:
            
            self.type = base.type
            self.black = base.black
            self.coordinates = (base.coordinates[0] - 1, base.coordinates[1] - 1)
            self.selected = False
        else:
            self.type = 'integer'
            self.black = 'base.black'
            self.coordinates = 'c'
            self.selected = 'stupid'

def check_mate(rows, king, color):
    black = (color == 'black')
    if black or not black:
        for row in rows:
            for square in row:
                if type(square) is not int:
                    if square.black == black:
                        for move in square.get_moves((row.index(square), rows.index(row))):
                            test_rows = [[Testpiece(square) for square in row] for row in rows]
                            current_x = row.index(square)
                            current_y = rows.index(row)
                            
                            test_rows[move[1]][move[0]] = test_rows[current_y][current_x]
                            test_rows[current_y][current_x] = 0
                            
                            kingf = (0, 0)
                            for row2 in rows:
                                for square2 in row2:
                                    if type(square2) is not int:
                                        if square2.type == 'king' and square2.black == black:
                                            kingf = (row2.index(square2), rows.index(row2))
                            
                            if square.type == 'king':
                                kingf = (move[1], move[1])
                            if not kingf == (0, 0): 
                                if black:  
                                    if check_king(test_rows, kingf, 'b') == False:
                                        print((current_x, current_y), ' to ', move)
                                        return False
                                else:
                                    if check_king(test_rows, kingf, 'w') == False:
                                        print((current_x, current_y), ' to ', move)
                                        return False
    return True

def check_check(rows, white_king, black_king, test = 'all') -> str:
    ret = [False, False]
    if test != 'black':
        white = check_king(rows, white_king, 'w')
        if white:
            ret[0] = True
       
    if test != 'white': 
        black = check_king(rows, black_king, 'b')
        if black:
            ret[1] = True
        
    return ret
            
def check_king(rows, king, c):
        
    black = (c == 'b')
    
    if black:
        left = get(king[1] + 1, king[0] - 1, rows)
        right = get(king[1] + 1, king[0] + 1, rows)
        
        if type(left) is not int and type(left) is not str and left.type != 'int':
            if left.type == 'pawn' and not left.black:
                return True
            
        if type(right) is not int and type(right) is not str and right.type != 'int':
            if right.type == 'pawn' and not right.black:
                return True
            
    else:
        left = get(king[1] - 1, king[0] - 1, rows)
        right = get(king[1] - 1, king[0] + 1, rows)
        
        if type(left) is not int and type(left) is not str and left.type != 'int':
            if left.type == 'pawn' and left.black:
                return True
            
        if type(right) is not int and type(right) is not str and right.type != 'int':
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
                else:
                    break
                
            x += x_inc
            y += y_inc
            square = get(y, x, rows)
        
    qb = ('queen', 'bishop')
    qr = ('queen', 'rrook', 'lrook')
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