# chess_gui.py
"""Chess AI với Pygame, Minimax + Alpha‑Beta, Iterative Deepening, Transposition Table

Yêu cầu: một file duy nhất, không dùng thư viện python‑chess.
"""

import pygame
import time
import sys
from collections import defaultdict

# ===== TIMEOUT MECHANISM =====
SEARCH_DEADLINE = None  # Set trước mỗi lần tìm kiếm
class SearchTimeout(Exception):
    pass

# ------------------------------------------------------------
# Cấu hình bàn cờ
# ------------------------------------------------------------
BOARD_SIZE = 8
SQUARE_SIZE = 80  # pixel
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE

# Đồ họa
WHITE_COLOR = (240, 217, 181)
GRAY_COLOR = (181, 136, 99)

# Đánh giá vật liệu
MATERIAL = {
    'K': 10000, 'Q': 900, 'R': 500, 'B': 330, 'N': 320, 'P': 100,
    'k': -10000, 'q': -900, 'r': -500, 'b': -330, 'n': -320, 'p': -100,
    '.': 0,
}

# ------------------------------------------------------------
# Piece‑Square Tables (PST) – từ bài giảng CS188
# ------------------------------------------------------------
PAWN_PST = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
KNIGHT_PST = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]
BISHOP_PST = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20],
]
ROOK_PST = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [0, 0, 0, 5, 5, 0, 0, 0],
]
QUEEN_PST = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20],
]
KING_PST_MID = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20],
]

PST = {
    'P': PAWN_PST,
    'N': KNIGHT_PST,
    'B': BISHOP_PST,
    'R': ROOK_PST,
    'Q': QUEEN_PST,
    'K': KING_PST_MID,
    'p': PAWN_PST,
    'n': KNIGHT_PST,
    'b': BISHOP_PST,
    'r': ROOK_PST,
    'q': QUEEN_PST,
    'k': KING_PST_MID,
}

# ------------------------------------------------------------
# Hình ảnh quân cờ – tải một lần
# ------------------------------------------------------------
pygame.init()
piece_images = {}
def load_piece_images():
    base_path = "pieces"
    for color in ("white", "black"):
        folder = f"{base_path}/{color}/"
        for name in ["K","Q","R","B","N","P","k","q","r","b","n","p"]:
            # file name pattern: {name}.svg (example) – pygame không hỗ trợ svg trực tiếp, dùng png nếu đã chuyển; giả sử có png.
            # Để đơn giản, dùng pygame.image.load, cho phép .png hoặc .svg nếu pygame‑sdl2 hỗ trợ.
            try:
                img = pygame.image.load(folder + name + ".png")
            except Exception:
                try:
                    img = pygame.image.load(folder + name + ".svg")
                except Exception:
                    continue
            piece_images[name] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
load_piece_images()

# ------------------------------------------------------------
# Bàn cờ khởi tạo
# ------------------------------------------------------------

def initial_board():
    # '.' cho ô trống
    board = [
        ['r','n','b','q','k','b','n','r'],
        ['p','p','p','p','p','p','p','p'],
        ['.']*8,
        ['.']*8,
        ['.']*8,
        ['.']*8,
        ['P','P','P','P','P','P','P','P'],
        ['R','N','B','Q','K','B','N','R'],
    ]
    return board

# ------------------------------------------------------------
# Hàm hỗ trợ
# ------------------------------------------------------------

def board_to_string(board):
    return ''.join(''.join(row) for row in board)

# ------------------------------------------------------------
# Đánh giá – bao gồm Material + PST + bonus đặc biệt
# ------------------------------------------------------------

def evaluate(board):
    """Đánh giá vị trí – dương có lợi cho trắng, âm cho đen"""
    # Kiểm tra Vua tồn tại
    white_king = any('K' in row for row in board)
    black_king = any('k' in row for row in board)
    if not white_king:
        return -99999
    if not black_king:
        return 99999

    material_score = 0
    pst_score = 0
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == '.':
                continue
            material_score += MATERIAL[piece]
            # PST: trắng dùng vị trí, đen dùng vị trí ngược (đảo ngược dọc)
            if piece.upper() in PST:
                table = PST[piece]
                if piece.isupper():
                    pst_score += table[r][c]
                else:
                    pst_score -= table[7-r][c]
    # Chống lặp cờ: nếu thế cờ đã xuất hiện >= 2 lần, coi như hòa (trả về 0)
    board_str = board_to_string(board)
    if position_history.get(board_str, 0) >= 2:
        return 0
    
    return material_score + pst_score

# ------------------------------------------------------------
# Di chuyển – tạo danh sách nước đi hợp lệ cho người chơi hiện tại
# ------------------------------------------------------------

def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8

# Độ di chuyển các quân
knight_dirs = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
bishop_dirs = [(-1,-1),(-1,1),(1,-1),(1,1)]
rook_dirs   = [(-1,0),(1,0),(0,-1),(0,1)]
queen_dirs  = bishop_dirs + rook_dirs
king_dirs   = queen_dirs

def generate_moves(board, is_white):
    """Trả về danh sách nước đi dạng ((r1,c1),(r2,c2))"""
    moves = []
    own = set('PNBRQK') if is_white else set('pnbrqk')
    opp = set('pnbrqk') if is_white else set('PNBRQK')
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == '.' or piece not in own:
                continue
            if piece.upper() == 'P':
                direction = -1 if piece.isupper() else 1
                start_row = 6 if piece.isupper() else 1
                # Tiến một bước
                nr = r + direction
                if in_bounds(nr,c) and board[nr][c] == '.':
                    moves.append(((r,c),(nr,c)))
                    # Tiến hai bước từ vị trí khởi đầu
                    if r == start_row:
                        nr2 = r + 2*direction
                        if board[nr2][c] == '.':
                            moves.append(((r,c),(nr2,c)))
                # Bắt chéo
                for dc in (-1,1):
                    nc = c + dc
                    if in_bounds(nr,nc) and board[nr][nc] in opp:
                        moves.append(((r,c),(nr,nc)))
                # (Không có en‑passant)
            elif piece.upper() == 'N':
                for dr,dc in knight_dirs:
                    nr, nc = r+dr, c+dc
                    if in_bounds(nr,nc) and board[nr][nc] not in own:
                        moves.append(((r,c),(nr,nc)))
            elif piece.upper() == 'B':
                for dr,dc in bishop_dirs:
                    nr, nc = r+dr, c+dc
                    while in_bounds(nr,nc):
                        target = board[nr][nc]
                        if target == '.':
                            moves.append(((r,c),(nr,nc)))
                        elif target in opp:
                            moves.append(((r,c),(nr,nc)))
                            break
                        else:  # own piece
                            break
                        nr += dr; nc += dc
            elif piece.upper() == 'R':
                for dr,dc in rook_dirs:
                    nr, nc = r+dr, c+dc
                    while in_bounds(nr,nc):
                        target = board[nr][nc]
                        if target == '.':
                            moves.append(((r,c),(nr,nc)))
                        elif target in opp:
                            moves.append(((r,c),(nr,nc)))
                            break
                        else:
                            break
                        nr += dr; nc += dc
            elif piece.upper() == 'Q':
                for dr,dc in queen_dirs:
                    nr, nc = r+dr, c+dc
                    while in_bounds(nr,nc):
                        target = board[nr][nc]
                        if target == '.':
                            moves.append(((r,c),(nr,nc)))
                        elif target in opp:
                            moves.append(((r,c),(nr,nc)))
                            break
                        else:
                            break
                        nr += dr; nc += dc
            elif piece.upper() == 'K':
                for dr,dc in king_dirs:
                    nr, nc = r+dr, c+dc
                    if in_bounds(nr,nc) and board[nr][nc] not in own:
                        moves.append(((r,c),(nr,nc)))
    return moves

def make_move(board, move):
    """Thực hiện nước đi và trả về board mới (không thay đổi board gốc)"""
    new_board = [row[:] for row in board]
    (r1,c1),(r2,c2) = move
    piece = new_board[r1][c1]
    new_board[r2][c2] = piece
    new_board[r1][c1] = '.'
    return new_board

# ------------------------------------------------------------
# Transposition Table
# ------------------------------------------------------------
TT_SIZE = 500000
transposition_table = {}
position_history = {}
HALF_MOVE_COUNTER = 0

# ------------------------------------------------------------
# Thuật toán Minimax + Alpha‑Beta với TT
# ------------------------------------------------------------

def alpha_beta(board, depth, alpha, beta, is_white_turn):
    """Minimax có cắt nhánh và tra cứu TT.
    Trả về giá trị đánh giá cho vị trí tại độ sâu depth.
    """
    # ===== CHECK TIMEOUT =====
    if SEARCH_DEADLINE is not None and time.time() > SEARCH_DEADLINE:
        raise SearchTimeout()
    
    # Lưu nguyên giá trị alpha/beta để xác định flag sau khi tính
    original_alpha, original_beta = alpha, beta

    board_key = (board_to_string(board), is_white_turn)
    entry = transposition_table.get(board_key)
    if entry and entry[0] >= depth:
        stored_depth, stored_score, flag, _ = entry
        if flag == 'EXACT':
            return stored_score
        if flag == 'LOWERBOUND' and stored_score > alpha:
            alpha = stored_score
        if flag == 'UPPERBOUND' and stored_score < beta:
            beta = stored_score
        if alpha >= beta:
            return stored_score

    # Kiểm tra kết thúc hoặc độ sâu 0
    white_king = any('K' in row for row in board)
    black_king = any('k' in row for row in board)
    if not white_king:
        return -99999
    if not black_king:
        return 99999
    if depth == 0:
        return evaluate(board)

    moves = generate_moves(board, is_white_turn)
    # Loại bỏ nước đi khiến Vua bị tấn công (King-into-check)
    safe_moves = []
    for move in moves:
        test_board = make_move(board, move)
        # Tìm vị trí Vua của bên đang đi
        king_char = 'K' if is_white_turn else 'k'
        king_pos = None
        for r in range(8):
            for c in range(8):
                if test_board[r][c] == king_char:
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        if king_pos is None:
            safe_moves.append(move)
            continue
        # Kiểm tra xem Vua có bị tấn công không
        opponent_moves = generate_moves(test_board, not is_white_turn)
        is_attacked = False
        for opp_move in opponent_moves:
            if opp_move[1] == king_pos:
                is_attacked = True
                break
        if not is_attacked:
            safe_moves.append(move)
    moves = safe_moves
    if not moves:
        # Không có nước đi hợp lệ → chiếu bí (đối phương thắng)
        return -90000 if is_white_turn else 90000

    # Nếu TT có best_move, đưa lên đầu
    if entry and entry[3] in moves:
        moves.remove(entry[3])
        moves.insert(0, entry[3])

    best_score = -float('inf') if is_white_turn else float('inf')
    best_move = None
    for move in moves:
        new_board = make_move(board, move)
        score = alpha_beta(new_board, depth-1, alpha, beta, not is_white_turn)
        if is_white_turn:
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
        else:
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, best_score)
        if beta <= alpha:
            break
    # Ghi vào TT
    if len(transposition_table) > TT_SIZE:
        # xóa một entry ngẫu nhiên (đơn giản)
        transposition_table.pop(next(iter(transposition_table)))
    # Xác định flag dựa trên so sánh với giá trị gốc
    if best_score <= original_alpha:
        flag = 'UPPERBOUND'
    elif best_score >= original_beta:
        flag = 'LOWERBOUND'
    else:
        flag = 'EXACT'
    transposition_table[board_key] = (depth, best_score, flag, best_move)
    return best_score

# ------------------------------------------------------------
# Iterative Deepening
# ------------------------------------------------------------

def find_best_move(board, is_white_turn, time_limit=2.0, max_depth=6, verbose=False):
    """Tìm kiếm nước đi tốt nhất bằng Iterative Deepening + Transposition Table."""
    global SEARCH_DEADLINE
    start = time.time()
    SEARCH_DEADLINE = start + time_limit
    best_move = None
    best_score = None
    for depth in range(1, max_depth + 1):
        if time.time() > SEARCH_DEADLINE:
            if verbose:
                print(f"Timeout before depth {depth}")
            break
        if verbose:
            print(f"Searching depth {depth}...")
        alpha = -float('inf')
        beta = float('inf')
        moves = generate_moves(board, is_white_turn)
        if not moves:
            return None
        board_key = (board_to_string(board), is_white_turn)
        entry = transposition_table.get(board_key)
        if entry and entry[3] in moves:
            moves.remove(entry[3])
            moves.insert(0, entry[3])
        local_best_move = None
        local_best_score = -float('inf') if is_white_turn else float('inf')
        try:
            for move in moves:
                if time.time() > SEARCH_DEADLINE:
                    raise SearchTimeout()
                new_board = make_move(board, move)
                score = alpha_beta(new_board, depth - 1, alpha, beta, not is_white_turn)
                if is_white_turn:
                    if score > local_best_score:
                        local_best_score = score
                        local_best_move = move
                    alpha = max(alpha, local_best_score)
                else:
                    if score < local_best_score:
                        local_best_score = score
                        local_best_move = move
                    beta = min(beta, local_best_score)
                if beta <= alpha:
                    break
        except SearchTimeout:
            if verbose:
                print(f"Timeout at depth {depth}")
            break
        if local_best_move is not None:
            best_move = local_best_move
            best_score = local_best_score
            if verbose:
                print(f"Best move: {best_move} (Score: {best_score})")
    return best_move



# ------------------------------------------------------------
# Vẽ giao diện Pygame
# ------------------------------------------------------------

def move_to_notation(move, board):
    """Chuyển ((r1,c1),(r2,c2)) sang ký hiệu cờ vua, ví dụ 'Nb1-c3'."""
    (r1, c1), (r2, c2) = move
    piece = board[r1][c1]
    col_from = chr(ord('a') + c1)
    row_from = str(8 - r1)
    col_to = chr(ord('a') + c2)
    row_to = str(8 - r2)
    return f"{piece}{col_from}{row_from}-{col_to}{row_to}"

def draw_board(screen, board):
    for r in range(8):
        for c in range(8):
            color = WHITE_COLOR if (r + c) % 2 == 0 else GRAY_COLOR
            pygame.draw.rect(screen, color, pygame.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = board[r][c]
            if piece != '.':
                img = piece_images.get(piece)
                if img:
                    screen.blit(img, (c*SQUARE_SIZE, r*SQUARE_SIZE))


def draw_score(screen, score):
    font = pygame.font.SysFont(None, 36)
    text = f"Score: {score}"
    color = (0,255,0) if score >= 0 else (255,0,0)
    img = font.render(text, True, color)
    screen.blit(img, (10,10))

# ------------------------------------------------------------
# Main loop
# ------------------------------------------------------------

def main():
    global SEARCH_DEADLINE, HALF_MOVE_COUNTER
    pygame.display.set_caption('Chess AI - AI vs AI')
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    clock = pygame.time.Clock()
    board = initial_board()
    is_white_turn = True
    running = True
    move_count = 1
    game_moves = []
    HALF_MOVE_COUNTER = 0
    position_history.clear()

    print("=== TRAN DAU BAT DAU ===")
    print(f"{'#':>3} {'Ben':<6} {'Nuoc di':<12} {'Diem'}")
    print("-" * 40)

    while running:
        # 1. Xử lý sự kiện thoát
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if not running:
            break

        # 2. Vẽ bàn cờ
        draw_board(screen, board)
        cur_score = evaluate(board)
        draw_score(screen, cur_score)
        pygame.display.flip()

        # 3. AI tìm nước đi
        move = find_best_move(board, is_white_turn, time_limit=2.0, max_depth=6, verbose=False)
        SEARCH_DEADLINE = None

        if move is None:
            print("Game over - no moves available.")
            time.sleep(3)
            break

        # 4. Lưu thông tin TRƯỚC KHI đi
        (r1, c1), (r2, c2) = move
        is_capture = board[r2][c2] != '.'
        is_pawn_move = board[r1][c1].upper() == 'P'
        notation = move_to_notation(move, board)
        side = "White" if is_white_turn else "Black"

        # 5. Thực hiện nước đi
        board = make_move(board, move)
        
        # 6. Cập nhật bộ đếm 50 nước và lịch sử thế cờ
        if is_pawn_move or is_capture:
            HALF_MOVE_COUNTER = 0
        else:
            HALF_MOVE_COUNTER += 1
        pos_key = board_to_string(board)
        position_history[pos_key] = position_history.get(pos_key, 0) + 1

        # 7. In ra màn hình và lưu log
        score_after = evaluate(board)
        line = f"{move_count:>3} {side:<6} {notation:<12} {score_after:+d}"
        print(line)
        game_moves.append(line)
        move_count += 1

        # ==========================================
        # 8. KIỂM TRA KẾT THÚC GAME (ĐẶT ĐÚNG VỊ TRÍ NÀY)
        # ==========================================
        if 'k' not in pos_key:
            print(f"\n=== TRANG THANG TAI NUOC {move_count - 1} (Den mat Vua) ===")
            running = False
            break
        if 'K' not in pos_key:
            print(f"\n=== DEN THANG TAI NUOC {move_count - 1} (Trang mat Vua) ===")
            running = False
            break
        if position_history[pos_key] >= 3:
            print(f"\n=== HOA DO LAP CO 3 LAN TAI NUOC {move_count - 1} ===")
            running = False
            break
        if HALF_MOVE_COUNTER >= 100:
            print(f"\n=== HOA DO LUAT 50 NUOC TAI NUOC {move_count - 1} ===")
            running = False
            break

        # 9. Chuyển lượt
        is_white_turn = not is_white_turn

        # 10. Chờ 0.5s nhưng không làm treo UI
        wait_start = time.time()
        while time.time() - wait_start < 0.5:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                    break
            clock.tick(30)

    # Ghi file log
    print("-" * 40)
    print(f"Tong so nuoc di: {move_count - 1}")
    with open("game_moves.txt", "w", encoding="utf-8") as f:
        f.write("=== LICH SU NUOC DI ===\n")
        f.write(f"{'#':>3} {'Ben':<6} {'Nuoc di':<12} {'Diem'}\n")
        f.write("-" * 40 + "\n")
        f.write("\n".join(game_moves))
        f.write(f"\n\nTong so nuoc di: {move_count - 1}\n")
    print("Da luu lich su vao file: game_moves.txt")

    pygame.quit()

if __name__ == "__main__":
    main()
