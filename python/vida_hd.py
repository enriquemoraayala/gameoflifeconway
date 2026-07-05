import sys
import numpy as np
import pygame


# ============================================================
# JUEGO DE LA VIDA - CONWAY HD
# Versión Python rápida para macOS moderno
# ============================================================

DEFAULT_COLS = 220
DEFAULT_ROWS = 130

MAX_COLS = 1200
MAX_ROWS = 700

MAX_WINDOW_W = 1500
MAX_WINDOW_H = 900
STATUS_H = 48

DEFAULT_SPEED = 30          # generaciones por segundo
RANDOM_DENSITY = 0.30       # equivalente aproximado a RND(1) > .7

BG = (8, 10, 14)
GRID_LINE = (28, 32, 38)
ALIVE = (70, 220, 120)
DEAD = (8, 10, 14)
TEXT = (230, 235, 240)
MUTED = (150, 160, 170)
CURSOR = (255, 80, 80)
STATUS_BG = (18, 22, 30)


PATTERNS = {
    "GOSPER GLIDER GUN": [
        (26, 2), (24, 3), (26, 3),
        (14, 4), (15, 4), (22, 4), (23, 4),
        (36, 4), (37, 4), (13, 5), (17, 5),
        (22, 5), (23, 5), (36, 5), (37, 5),
        (2, 6), (3, 6), (12, 6), (18, 6),
        (22, 6), (23, 6), (2, 7), (3, 7),
        (12, 7), (16, 7), (18, 7), (19, 7),
        (24, 7), (26, 7), (12, 8), (18, 8),
        (26, 8), (13, 9), (17, 9), (14, 10), (15, 10),
    ],
    "PULSAR": [
        (15, 5), (16, 5), (17, 5), (21, 5), (22, 5), (23, 5),
        (13, 7), (18, 7), (20, 7), (25, 7),
        (13, 8), (18, 8), (20, 8), (25, 8),
        (13, 9), (18, 9), (20, 9), (25, 9),
        (15, 10), (16, 10), (17, 10), (21, 10), (22, 10), (23, 10),
        (15, 12), (16, 12), (17, 12), (21, 12), (22, 12), (23, 12),
        (13, 13), (18, 13), (20, 13), (25, 13),
        (13, 14), (18, 14), (20, 14), (25, 14),
        (13, 15), (18, 15), (20, 15), (25, 15),
        (15, 17), (16, 17), (17, 17), (21, 17), (22, 17), (23, 17),
    ],
    "ACORN": [
        (17, 10), (19, 11), (16, 12), (17, 12),
        (20, 12), (21, 12), (22, 12),
    ],
}


def life_step(grid: np.ndarray) -> np.ndarray:
    """
    Calcula una generación del Juego de la Vida.
    Usa bordes toroidales, igual que el BASIC original:
    salir por un borde entra por el contrario.
    """
    g = grid.astype(np.int8)

    n = (
        np.roll(np.roll(g, -1, 0), -1, 1) +
        np.roll(np.roll(g, -1, 0),  0, 1) +
        np.roll(np.roll(g, -1, 0),  1, 1) +
        np.roll(np.roll(g,  0, 0), -1, 1) +
        np.roll(np.roll(g,  0, 0),  1, 1) +
        np.roll(np.roll(g,  1, 0), -1, 1) +
        np.roll(np.roll(g,  1, 0),  0, 1) +
        np.roll(np.roll(g,  1, 0),  1, 1)
    )

    return (n == 3) | (grid & (n == 2))


def place_pattern(grid: np.ndarray, cells: list[tuple[int, int]]) -> None:
    """
    Coloca un patrón centrado en la rejilla actual.
    Las coordenadas originales del BASIC se normalizan y se centran.
    """
    if not cells:
        return

    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    pattern_w = max_x - min_x + 1
    pattern_h = max_y - min_y + 1

    h, w = grid.shape

    off_x = max(0, (w - pattern_w) // 2)
    off_y = max(0, (h - pattern_h) // 2)

    for x, y in cells:
        px = off_x + (x - min_x)
        py = off_y + (y - min_y)
        if 0 <= px < w and 0 <= py < h:
            grid[py, px] = True


def make_random_grid(cols: int, rows: int) -> np.ndarray:
    rng = np.random.default_rng()
    return rng.random((rows, cols)) < RANDOM_DENSITY


def calc_cell_size(cols: int, rows: int) -> int:
    cell_w = MAX_WINDOW_W // cols
    cell_h = (MAX_WINDOW_H - STATUS_H) // rows
    return max(1, min(10, cell_w, cell_h))


def draw_text(surface, font, text, x, y, color=TEXT):
    img = font.render(text, True, color)
    surface.blit(img, (x, y))


def draw_centered(surface, font, text, y, color=TEXT):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(img, rect)


def open_menu_window():
    pygame.display.set_mode((860, 560))
    pygame.display.set_caption("Juego de la Vida - Conway HD")


def menu(title, options, footer="Q / ESC: salir"):
    """
    options: lista de tuplas:
    [
        ("1", "Texto visible", valor),
        ...
    ]
    """
    open_menu_window()
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("Menlo", 36, bold=True)
    font = pygame.font.SysFont("Menlo", 24)
    small = pygame.font.SysFont("Menlo", 18)

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return "quit"

                key = event.unicode.upper()
                for opt_key, _, value in options:
                    if key == opt_key.upper():
                        return value

        screen.fill(BG)

        draw_centered(screen, title_font, title, 90)

        y = 180
        for opt_key, label, _ in options:
            draw_text(screen, font, f"{opt_key}: {label}", 220, y)
            y += 46

        draw_centered(screen, small, footer, 500, MUTED)

        pygame.display.flip()


def ask_number(title, minimum, maximum, default):
    open_menu_window()
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("Menlo", 32, bold=True)
    font = pygame.font.SysFont("Menlo", 26)
    small = pygame.font.SysFont("Menlo", 18)

    value = str(default)

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None

                if event.key == pygame.K_RETURN:
                    if value:
                        n = int(value)
                        if minimum <= n <= maximum:
                            return n

                elif event.key == pygame.K_BACKSPACE:
                    value = value[:-1]

                elif event.unicode.isdigit():
                    value += event.unicode

        screen.fill(BG)

        draw_centered(screen, title_font, title, 120)
        draw_centered(screen, small, f"Rango: {minimum} - {maximum}", 170, MUTED)

        box = pygame.Rect(260, 240, 340, 58)
        pygame.draw.rect(screen, STATUS_BG, box, border_radius=8)
        pygame.draw.rect(screen, MUTED, box, width=2, border_radius=8)

        shown = value if value else "_"
        draw_centered(screen, font, shown, 270)

        draw_centered(screen, small, "RETURN: aceptar    BACKSPACE: borrar    ESC: cancelar", 430, MUTED)

        pygame.display.flip()


def grid_to_surface(grid: np.ndarray) -> pygame.Surface:
    """
    Convierte una matriz booleana en una superficie Pygame.
    Mucho más rápido que dibujar rectángulo por rectángulo.
    """
    h, w = grid.shape
    img = np.empty((h, w, 3), dtype=np.uint8)
    img[:, :] = DEAD
    img[grid] = ALIVE

    # Pygame espera array con forma ancho x alto x RGB
    return pygame.surfarray.make_surface(np.swapaxes(img, 0, 1))


def draw_simulation(screen, grid, cell, cx, cy, gen, gmax, speed, playing, finished):
    h, w = grid.shape

    screen.fill(BG)

    base = grid_to_surface(grid)

    if cell > 1:
        scaled = pygame.transform.scale(base, (w * cell, h * cell))
        screen.blit(scaled, (0, 0))
    else:
        screen.blit(base, (0, 0))

    # Líneas de rejilla solo cuando hay tamaño suficiente.
    if cell >= 6 and w <= 260 and h <= 180:
        for x in range(0, w * cell + 1, cell):
            pygame.draw.line(screen, GRID_LINE, (x, 0), (x, h * cell))
        for y in range(0, h * cell + 1, cell):
            pygame.draw.line(screen, GRID_LINE, (0, y), (w * cell, y))

    # Cursor en modo edición / pausa.
    if not playing and not finished:
        rect = pygame.Rect(cx * cell, cy * cell, cell, cell)
        pygame.draw.rect(screen, CURSOR, rect, width=max(1, min(3, cell)))

    status_y = h * cell
    pygame.draw.rect(screen, STATUS_BG, (0, status_y, screen.get_width(), STATUS_H))

    font = pygame.font.SysFont("Menlo", 17)

    if finished:
        msg = f"FIN  GEN:{gen}/{gmax}   Q=MENU"
    elif playing:
        msg = f"GEN:{gen}/{gmax}   VELOCIDAD:{speed}/s   P=PAUSA   +/-=VEL   Q=MENU"
    else:
        msg = (
            f"EDICION  GEN:{gen}/{gmax}   WASD/CURSORES=MOVER   "
            f"ESPACIO=CAMBIA   RATON=EDITA   RETURN=EMPIEZA   Q=MENU"
        )

    draw_text(screen, font, msg, 12, status_y + 14)


def run_simulation(grid: np.ndarray, gmax: int):
    rows, cols = grid.shape
    cell = calc_cell_size(cols, rows)

    width = cols * cell
    height = rows * cell + STATUS_H

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(f"Juego de la Vida HD - {cols}x{rows}")

    clock = pygame.time.Clock()

    cx = cols // 2
    cy = rows // 2

    gen = 0
    speed = DEFAULT_SPEED
    playing = False
    finished = False

    elapsed = 0.0
    mouse_painting = None

    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return "menu"

                if event.key == pygame.K_RETURN:
                    if not finished:
                        playing = True

                elif event.key == pygame.K_p:
                    if not finished:
                        playing = not playing

                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    speed = min(1000, speed + 5)

                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    speed = max(1, speed - 5)

                elif not playing and not finished:
                    if event.key in (pygame.K_w, pygame.K_UP):
                        cy = (cy - 1) % rows

                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        cy = (cy + 1) % rows

                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        cx = (cx - 1) % cols

                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        cx = (cx + 1) % cols

                    elif event.key == pygame.K_SPACE:
                        grid[cy, cx] = not grid[cy, cx]

                    elif event.key == pygame.K_c:
                        grid[:, :] = False
                        gen = 0
                        finished = False

                    elif event.key == pygame.K_r:
                        grid[:, :] = make_random_grid(cols, rows)
                        gen = 0
                        finished = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not playing and not finished:
                    mx, my = event.pos
                    gx = mx // cell
                    gy = my // cell

                    if 0 <= gx < cols and 0 <= gy < rows:
                        cx, cy = gx, gy

                        if event.button == 1:
                            grid[gy, gx] = not grid[gy, gx]
                            mouse_painting = True
                        elif event.button == 3:
                            grid[gy, gx] = False
                            mouse_painting = False

            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_painting = None

            elif event.type == pygame.MOUSEMOTION:
                if not playing and not finished and mouse_painting is not None:
                    mx, my = event.pos
                    gx = mx // cell
                    gy = my // cell

                    if 0 <= gx < cols and 0 <= gy < rows:
                        cx, cy = gx, gy
                        grid[gy, gx] = mouse_painting

        if playing and not finished:
            elapsed += dt
            step_time = 1.0 / speed

            while elapsed >= step_time and playing and not finished:
                grid = life_step(grid)
                gen += 1
                elapsed -= step_time

                if gen >= gmax:
                    playing = False
                    finished = True

        draw_simulation(screen, grid, cell, cx, cy, gen, gmax, speed, playing, finished)
        pygame.display.flip()


def configure_pattern():
    selected = menu(
        "CONFIGURACIONES",
        [
            ("1", "Gosper Glider Gun", "GOSPER GLIDER GUN"),
            ("2", "Pulsar", "PULSAR"),
            ("3", "Acorn", "ACORN"),
        ],
        footer="1-3: elegir patrón    Q / ESC: salir",
    )

    if selected in ("quit", None):
        return None, None

    cols = ask_number("COLUMNAS", 10, MAX_COLS, DEFAULT_COLS)
    if cols is None:
        return None, None

    rows = ask_number("FILAS", 10, MAX_ROWS, DEFAULT_ROWS)
    if rows is None:
        return None, None

    gmax = ask_number("GENERACIONES", 1, 1_000_000, 9999)
    if gmax is None:
        return None, None

    grid = np.zeros((rows, cols), dtype=bool)
    place_pattern(grid, PATTERNS[selected])

    return grid, gmax


def configure_custom():
    mode = menu(
        "CUSTOM GRID",
        [
            ("1", "Custom vacío", "custom"),
            ("2", "Random", "random"),
        ],
        footer="1-2: elegir modo    Q / ESC: salir",
    )

    if mode in ("quit", None):
        return None, None

    cols = ask_number("COLUMNAS", 10, MAX_COLS, 220)
    if cols is None:
        return None, None

    rows = ask_number("FILAS", 10, MAX_ROWS, 130)
    if rows is None:
        return None, None

    gmax = ask_number("GENERACIONES", 1, 1_000_000, 9999)
    if gmax is None:
        return None, None

    if mode == "random":
        grid = make_random_grid(cols, rows)
    else:
        grid = np.zeros((rows, cols), dtype=bool)

    return grid, gmax


def main():
    pygame.init()

    try:
        while True:
            choice = menu(
                "JUEGO DE LA VIDA - CONWAY HD",
                [
                    ("1", "Cargar configuraciones", "patterns"),
                    ("2", "Custom grid", "custom"),
                ],
                footer="1-2: elegir    Q / ESC: salir",
            )

            if choice in ("quit", None):
                break

            if choice == "patterns":
                grid, gmax = configure_pattern()
            else:
                grid, gmax = configure_custom()

            if grid is None:
                continue

            result = run_simulation(grid, gmax)

            if result == "quit":
                break

    finally:
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()