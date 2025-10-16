import random
from PIL import Image, ImageDraw

width = 52  # largura da grade de contribuição
height = 7  # altura da grade
cell_size = 10  # tamanho de cada célula
frames = 800
fps = 15

# Cores de blocos estilo Tetris
colors = ["#00BCD4", "#FF9800", "#8BC34A", "#E91E63", "#9C27B0", "#FFC107", "#3F51B5"]

# Matriz inicial vazia
grid = [[0 for _ in range(width)] for _ in range(height)]

def drop_piece():
    """Simula uma peça caindo na grade."""
    col = random.randint(0, width - 1)
    color = random.choice(colors)
    for row in range(height):
        # apaga posição anterior
        if row > 0:
            grid[row - 1][col] = 0
        # desenha posição atual
        grid[row][col] = color
        yield

    # 'peça' fixa na última linha
    grid[height - 1][col] = color

def clear_lines():
    """Apaga linhas completas (efeito Tetris)."""
    global grid
    new_grid = [row for row in grid if any(cell == 0 for cell in row)]
    cleared = height - len(new_grid)
    if cleared > 0:
        for _ in range(cleared):
            new_grid.insert(0, [0 for _ in range(width)])
        grid = new_grid

def draw_frame():
    """Desenha um frame da grade."""
    img = Image.new("RGB", (width * cell_size, height * cell_size), (240, 240, 240))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        for x in range(width):
            if grid[y][x] != 0:
                draw.rectangle(
                    [x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size],
                    fill=grid[y][x]
                )
    return img

# Geração dos frames
images = []
for i in range(frames):
    if i % 30 == 0:  # a cada 30 frames, solta uma nova peça
        piece = drop_piece()
    try:
        next(piece)
    except StopIteration:
        clear_lines()
    images.append(draw_frame())

# Salvar como GIF animado
images[0].save(
    "tetris.gif",
    save_all=True,
    append_images=images[1:],
    duration=int(1000 / fps),
    loop=0
)
print(f"Tetris gerado com {frames} frames e {fps} FPS.")
