#!/usr/bin/env python3
"""
Gera um GIF animado estilo Tetris em uma grade 53x7 (semelhante ao calendário de contribuições).
Dependência: Pillow
Uso: python generate_tetris.py --out tetris.gif --frames 800 --fps 15
"""

import argparse
import random
from PIL import Image, ImageDraw

# Configuração da grade (semelhante ao contribution heatmap)
WEEKS = 53
DAYS = 7

CELL = 12          # tamanho do bloco (px)
GAP = 2            # espaço entre blocos
MARGIN = 8         # margem em volta
WIDTH = MARGIN*2 + WEEKS * (CELL + GAP) - GAP
HEIGHT = MARGIN*2 + DAYS * (CELL + GAP) - GAP

# Cores para tetrominos
COLORS = {
    'I': (102, 204, 255),
    'O': (255, 204, 102),
    'T': (204, 153, 255),
    'S': (153, 255, 153),
    'Z': (255, 153, 153),
    'J': (153, 179, 255),
    'L': (255, 204, 179),
    'BG': (246, 248, 250),  # fundo
    'GRID': (230, 235, 240),
    'OUTLINE': (200, 200, 200),
}

# Tetromino formas (listas de (x,y) offsets)
TETROMINOS = {
    'I': [(0,0),(1,0),(2,0),(3,0)],
    'O': [(0,0),(1,0),(0,1),(1,1)],
    'T': [(0,0),(1,0),(2,0),(1,1)],
    'S': [(1,0),(2,0),(0,1),(1,1)],
    'Z': [(0,0),(1,0),(1,1),(2,1)],
    'J': [(0,0),(0,1),(1,1),(2,1)],
    'L': [(2,0),(0,1),(1,1),(2,1)],
}

def cell_to_px(col, row):
    """Converte coluna (0..WEEKS-1) e linha (0..DAYS-1) para bbox em px."""
    x = MARGIN + col * (CELL + GAP)
    y = MARGIN + row * (CELL + GAP)
    return x, y, x + CELL, y + CELL

def draw_grid(draw):
    # fundo
    draw.rectangle([(0,0),(WIDTH,HEIGHT)], fill=COLORS['BG'])
    # grade (opcional estilos semelhantes ao Github)
    for c in range(WEEKS):
        for r in range(DAYS):
            x1,y1,x2,y2 = cell_to_px(c,r)
            draw.rectangle([x1,y1,x2,y2], fill=COLORS['GRID'], outline=None)

def place_piece_on_board(board, piece_name, x, y, rotation=0):
    """Tenta colocar tetromino no board (board é DAYS x WEEKS, rows = 7)."""
    offsets = TETROMINOS[piece_name]
    coords = []
    for ox, oy in offsets:
        rx, ry = ox, oy
        # rotações simples (90 deg * rotation)
        for _ in range(rotation % 4):
            rx, ry = -ry, rx
        col = x + rx
        row = y + ry
        if not (0 <= col < WEEKS and 0 <= row < DAYS):
            return False, []
        if board[row][col] != None:
            return False, []
        coords.append((row, col))
    for row, col in coords:
        board[row][col] = piece_name
    return True, coords

def render_board(board, highlight=None):
    """Renderiza board (DAYS x WEEKS) para imagem PIL. highlight = list de (row,col,color) para peça em queda."""
    im = Image.new('RGBA', (WIDTH, HEIGHT), COLORS['BG'])
    draw = ImageDraw.Draw(im)
    draw_grid(draw)
    # desenha células preenchidas
    for r in range(DAYS):
        for c in range(WEEKS):
            val = board[r][c]
            if val:
                x1,y1,x2,y2 = cell_to_px(c, r)
                draw.rectangle([x1, y1, x2, y2], fill=COLORS[val], outline=COLORS['OUTLINE'])
    # peça em queda (highlight)
    if highlight:
        for (r,c), color in highlight:
            x1,y1,x2,y2 = cell_to_px(c, r)
            draw.rectangle([x1, y1, x2, y2], fill=color, outline=COLORS['OUTLINE'])
    return im

def generate_frames(frames=200):
    # board inicial vazio: board[row][col] (row 0..6)
    board = [[None for _ in range(WEEKS)] for __ in range(DAYS)]
    images = []
    steps = 0
    col_cursor = 0

    while steps < frames:
        # escolhe peça
        piece = random.choice(list(TETROMINOS.keys()))
        rotation = random.randint(0,3)
        # spawn na coluna corrente (tenta não sair da grade)
        spawn_col = col_cursor
        # ajuste se necessário: limita spawn dentro da largura do tetromino
        piece_w = max(x for x,y in TETROMINOS[piece]) - min(x for x,y in TETROMINOS[piece]) + 1
        if spawn_col + piece_w > WEEKS:
            spawn_col = WEEKS - piece_w
        # faz peça "cair" do topo (row negativa simulado)
        y = -4  # começa acima
        while True:
            # calcula highlight coords (peça na posição atual)
            highlight = []
            valid = True
            for ox, oy in TETROMINOS[piece]:
                rx, ry = ox, oy
                for _ in range(rotation % 4):
                    rx, ry = -ry, rx
                col = spawn_col + rx
                row = y + ry
                if 0 <= row < DAYS and 0 <= col < WEEKS:
                    highlight.append(((row, col), COLORS[piece]))
                if row >= DAYS:
                    valid = False
            # render frame with highlight
            images.append(render_board(board, highlight))
            steps += 1
            if steps >= frames:
                break
            # tenta mover pra baixo
            # verifica colisão se mover y+1
            collision = False
            for ox, oy in TETROMINOS[piece]:
                rx, ry = ox, oy
                for _ in range(rotation % 4):
                    rx, ry = -ry, rx
                col = spawn_col + rx
                row = y + ry + 1
                if row >= DAYS:
                    collision = True
                    break
                if 0 <= row < DAYS and 0 <= col < WEEKS and board[row][col] is not None:
                    collision = True
                    break
            if collision:
                # fixa a peça na linha mais baixa possível: se y < 0, tentamos empurrar pra cima (simples)
                placed_ok, coords = place_piece_on_board(board, piece, spawn_col, y, rotation)
                # se não conseguir colocar (ex: topo cheio), encontramos uma coluna alternativa
                if not placed_ok:
                    # procura primeiro espaço vazio em colunas próximas
                    placed = False
                    for alt in range(WEEKS):
                        tx = (spawn_col + alt) % WEEKS
                        ok, _ = place_piece_on_board(board, piece, tx, 0, rotation)
                        if ok:
                            placed = True
                            break
                    if not placed:
                        # board full-ish, apenas renderiza e termina early
                        return images
                # avança cursor de coluna
                col_cursor = (col_cursor + random.randint(1,4)) % WEEKS
                break
            else:
                y += 1
                if steps >= frames:
                    break
        if steps >= frames:
            break
    return images

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='tetris.gif')
    parser.add_argument('--frames', type=int, default=200)
    args = parser.parse_args()

    frames = generate_frames(frames=args.frames)
    # salva GIF
    if frames:
        frames[0].save(
            args.out,
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=80,
            loop=0
        )
        print(f'GIF salvo em {args.out} com {len(frames)} frames.')
    else:
        print('Nenhum frame gerado.')

if __name__ == '__main__':
    main()
