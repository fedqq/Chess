import Utils

get = Utils._get
flip_list = Utils._flip_list

def test_move(original_rows, start_move = 0, end_move = 0, test = 'all', flipped = False):
    rows = [[Utils._TestPiece(square) for square in row] for row in original_rows]
    
    if flipped:
        rows = [row[::-1] for row in rows][::-1]
        if not end_move == start_move:
            end_move = flip_list(end_move)
            start_move = flip_list(start_move)
    
    if not start_move == end_move:
        rows[end_move[1]][end_move[0]] = rows[start_move[1]][start_move[0]]
        rows[start_move[1]][start_move[0]] = 0
        
    ret = [False, False]
    
    if test != 'black':
        for row_index, row in enumerate(rows):
            for square_index, square in enumerate(row):
                if type(square) is not int and square.type != 'int':
                    if square.type == 'king' and not square.black:
                        ret[0] = _check_king(rows, (square_index, row_index), black = False)
                        break
                        
    if test != 'white':
        for row_index, row in enumerate(rows):
            for square_index, square in enumerate(row):
                if type(square) is not int and square.type != 'int':
                    if square.type == 'king' and square.black:
                        ret[1] = _check_king(rows, (square_index, row_index), black = True)
                        break
         
    return ret

def _check_king(rows, king, black):
    
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
    qr = ('queen', 'rook')
    checks = [(1, -1, qb), (-1, 1, qb), (1, 1, qb), (-1, -1, qb), (-1, 0, qr), (1, 0, qr), (0, 1, qr), (0, -1, qr)]
    for check in checks:
        if check_moves(check[0], check[1], check[2]):
            return True
    
    if black:
        pawn_step = 1
    else:
        pawn_step = -   1

    left_piece = get(rows, king[1] + pawn_step, king[0] - 1)
    right_piece = get(rows, king[1] + pawn_step, king[0] + 1)
    
    if type(left_piece) is Utils._TestPiece and left_piece.type != 'int':
        if left_piece.type == 'pawn' and left_piece.black != black:
            return True
        
    if type(right_piece) is not int and type(right_piece) is not str and right_piece.type != 'int':
        if right_piece.type == 'pawn' and right_piece.black != black:
            return True
    
    for possible_knight in Utils._moves_dict['knight'][:-1]:
        
        possible_knight_position = (possible_knight[0] + king[0], possible_knight[1] + king[1])
        square = get(rows, possible_knight_position[1], possible_knight_position[0])
        if type(square) is not int and square != 'NA':
            if square.type == 'knight':
                if square.black != black:
                    return True
        
    return False