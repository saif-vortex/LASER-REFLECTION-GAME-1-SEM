import random

import pygame

# Start Pygame
pygame.init()

# ---------------- SETTINGS ----------------

CELL = 70
COLS = 9
ROWS = 7
TOP = 90

WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + TOP + 50

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Laser Maze - Reflection of Light")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 23)

# Colors
BLACK = (20, 25, 40)
WHITE = (240, 240, 240)
GREY = (90, 100, 120)
BLUE = (70, 160, 255)
RED = (255, 75, 85)
GREEN = (70, 230, 130)
YELLOW = (255, 220, 70)
DARK = (35, 42, 60)


def make_backdrop():
    backdrop = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        shade = y / HEIGHT
        color = (
            int(12 + 8 * shade),
            int(18 + 10 * shade),
            int(32 + 18 * shade),
        )
        pygame.draw.line(backdrop, color, (0, y), (WIDTH, y))

    stars = random.Random(12)
    for _ in range(95):
        x = stars.randrange(WIDTH)
        y = stars.randrange(HEIGHT)
        radius = stars.choice((1, 1, 1, 2))
        pygame.draw.circle(backdrop, (35, 49, 72), (x, y), radius)
    return backdrop


backdrop = make_backdrop()

# ---------------- GAME OBJECTS ----------------

levels = [
    {
        "source": (0, 3),
        "target": (6, 3),
        "mirrors": {(2, 3): "/", (2, 1): "/", (6, 1): "\\"},
        "obstacles": {(4, 2), (4, 4), (7, 4)},
    },
    {
        "source": (0, 5),
        "target": (6, 2),
        "mirrors": {(2, 5): "/", (2, 2): "/", (6, 2): "\\", (6, 5): "/"},
        "obstacles": {(4, 1), (4, 4), (7, 3)},
    },
    {
        "source": (0, 1),
        "target": (1, 2),
        "mirrors": {(3, 1): "\\", (3, 5): "/", (1, 5): "\\"},
        "obstacles": {(5, 2), (5, 4), (7, 3)},
    },
    {
        "source": (0, 2),
        "target": (6, 1),
        "mirrors": {(2, 2): "\\", (2, 5): "\\", (6, 5): "/"},
        "obstacles": {(4, 1), (4, 3), (7, 4)},
    },
]

level_index = 0
starting_mirrors = {}


def load_level(index):
    global source, target, mirrors, obstacles, starting_mirrors

    level = levels[index]
    source = level["source"]
    target = level["target"]
    obstacles = level["obstacles"].copy()

    available_cells = [
        (col, row)
        for row in range(ROWS)
        for col in range(COLS)
        if (col, row) not in obstacles
        and (col, row) != source
        and (col, row) != target
    ]
    mirror_count = len(level["mirrors"])
    random_cells = random.sample(available_cells, mirror_count)
    mirrors = {
        cell: random.choice(("/", "\\"))
        for cell in random_cells
    }
    starting_mirrors = mirrors.copy()


load_level(level_index)
dragging_mirror = None
dragging_mouse_pos = None

# ---------------- PHYSICS ----------------

def trace_laser():
    """Trace the laser and calculate its reflections."""

    x, y = source

    # Direction: right = (1, 0)
    dx, dy = 1, 0

    path = [(x, y)]
    visited = set()
    hit_target = False

    # Prevent an infinite loop if mirrors form a cycle.
    for step in range(300):

        # Move into the next cell.
        x += dx
        y += dy

        # Stop if the laser leaves the board.
        if x < 0 or x >= COLS or y < 0 or y >= ROWS:
            break

        path.append((x, y))

        # Check if the laser reaches its target.
        if (x, y) == target:
            hit_target = True
            break

        # Stop when the beam hits an obstacle.
        if (x, y) in obstacles:
            break

        # Stop if the laser repeats the same position
        # with the same direction.
        state = (x, y, dx, dy)

        if state in visited:
            break

        visited.add(state)

        # Apply the law of reflection at a mirror.
        if (x, y) in mirrors:
            mirror = mirrors[(x, y)]

            if mirror == "/":
                # Slash mirror:
                # right -> up, down -> left, etc.
                dx, dy = -dy, -dx

            else:
                # Backslash mirror:
                # right -> down, up -> left, etc.
                dx, dy = dy, dx

    return path, hit_target


# ---------------- DRAWING ----------------

def cell_center(cell):
    """Return the screen coordinates of a grid cell."""
    x, y = cell
    return (
        x * CELL + CELL // 2,
        TOP + y * CELL + CELL // 2
    )


def draw_game():
    screen.blit(backdrop, (0, 0))

    # Title and instructions.
    pygame.draw.rect(screen, (18, 27, 45), (0, 0, WIDTH, TOP - 8))
    pygame.draw.line(screen, (49, 79, 112), (0, TOP - 8), (WIDTH, TOP - 8), 2)
    title = font.render(f"LASER MAZE  /  LEVEL {level_index + 1}", True, WHITE)
    screen.blit(title, (18, 11))

    instructions = small_font.render(
        "Drag mirrors | Right-click: rotate | R: reset | SPACE: next | ESC: quit",
        True, (155, 179, 207)
    )
    screen.blit(instructions, (19, 51))
    pygame.draw.circle(screen, (85, 230, 177), (WIDTH - 22, 25), 5)

    # Draw the grid.
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(
                col * CELL, TOP + row * CELL,
                CELL, CELL
            )
            tile_color = (29, 42, 63) if (row + col) % 2 else (33, 47, 69)
            pygame.draw.rect(screen, tile_color, rect)
            pygame.draw.rect(screen, (43, 61, 85), rect, 1)
            pygame.draw.line(
                screen, (39, 54, 76),
                (rect.left + 8, rect.top + 9),
                (rect.right - 9, rect.top + 9), 1
            )
            pygame.draw.circle(
                screen, (48, 67, 92),
                (rect.left + 7, rect.bottom - 7), 1
            )

    # Draw obstacles.
    for cell in obstacles:
        cx, cy = cell_center(cell)
        shadow = pygame.Rect(cx - 21, cy - 17, 42, 42)
        pygame.draw.rect(screen, (12, 18, 30), shadow, border_radius=7)
        block = pygame.Rect(cx - 21, cy - 21, 42, 42)
        pygame.draw.rect(
            screen, (74, 89, 111), block, border_radius=7
        )
        pygame.draw.rect(
            screen, (119, 137, 161), block, 2, border_radius=7
        )
        pygame.draw.line(screen, (145, 159, 178), (cx - 13, cy - 12), (cx + 13, cy - 12), 2)
        for offset in (-8, 0, 8):
            pygame.draw.line(
                screen, (46, 59, 79),
                (cx - 12, cy + offset), (cx + 12, cy + offset), 2
            )

    # Draw the target.
    tx, ty = cell_center(target)
    pygame.draw.circle(screen, (87, 37, 62), (tx, ty), 29)
    pygame.draw.circle(screen, (255, 90, 119), (tx, ty), 25, 2)
    pygame.draw.circle(screen, (82, 35, 54), (tx, ty), 19)
    pygame.draw.circle(screen, (255, 224, 215), (tx, ty), 14)
    pygame.draw.circle(screen, (255, 90, 105), (tx, ty), 9)
    pygame.draw.circle(screen, (255, 194, 170), (tx - 3, ty - 4), 3)

    # Draw the laser source.
    sx, sy = cell_center(source)
    pygame.draw.circle(screen, (31, 73, 121), (sx, sy), 29)
    pygame.draw.circle(screen, (78, 179, 255), (sx, sy), 25, 2)
    pygame.draw.circle(screen, (41, 113, 177), (sx, sy), 18)
    pygame.draw.circle(screen, (152, 223, 255), (sx, sy), 10)
    pygame.draw.circle(screen, WHITE, (sx, sy), 5)

    # Calculate and draw the laser path.
    path, hit_target = trace_laser()

    points = [cell_center(cell) for cell in path]

    if len(points) > 1:
        beam_color = (90, 255, 207) if hit_target else (255, 83, 112)
        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.lines(glow, (*beam_color, 38), False, points, 18)
        pygame.draw.lines(glow, (*beam_color, 72), False, points, 10)
        screen.blit(glow, (0, 0))
        pygame.draw.lines(screen, beam_color, False, points, 4)
        pygame.draw.lines(screen, (255, 235, 211), False, points, 1)

    # Draw mirrors.
    for cell, orientation in mirrors.items():
        cx, cy = cell_center(cell)
        if cell == dragging_mirror and dragging_mouse_pos is not None:
            cx, cy = dragging_mouse_pos

        plate = pygame.Rect(cx - 26, cy - 26, 52, 52)
        pygame.draw.rect(screen, (13, 21, 35), plate.move(0, 3), border_radius=9)
        pygame.draw.rect(screen, (49, 69, 91), plate, border_radius=9)
        pygame.draw.rect(screen, (105, 131, 157), plate, 2, border_radius=9)
        pygame.draw.circle(screen, (171, 192, 209), (cx - 18, cy - 18), 2)
        pygame.draw.circle(screen, (171, 192, 209), (cx + 18, cy - 18), 2)
        pygame.draw.circle(screen, (171, 192, 209), (cx - 18, cy + 18), 2)
        pygame.draw.circle(screen, (171, 192, 209), (cx + 18, cy + 18), 2)

        if orientation == "/":
            start = (cx - 17, cy + 17)
            end = (cx + 17, cy - 17)
        else:
            start = (cx - 17, cy - 17)
            end = (cx + 17, cy + 17)

        pygame.draw.line(screen, (18, 28, 44), (start[0], start[1] + 3), (end[0], end[1] + 3), 12)
        pygame.draw.line(screen, (90, 231, 247), start, end, 10)
        pygame.draw.line(screen, (220, 255, 255), start, end, 4)

    # Display the game result.
    if hit_target:
        if level_index == len(levels) - 1:
            result = "ALL LEVELS COMPLETE!"
        else:
            result = "LEVEL COMPLETE! Press SPACE for next level"
        color = (106, 255, 198)
    else:
        result = "Rotate the mirrors to reach the target!"
        color = (184, 201, 222)

    result_text = font.render(result, True, color)
    result_panel = pygame.Rect(10, HEIGHT - 43, WIDTH - 20, 34)
    pygame.draw.rect(screen, (17, 28, 46), result_panel, border_radius=8)
    pygame.draw.rect(screen, (52, 75, 101), result_panel, 1, border_radius=8)
    screen.blit(result_text, (20, HEIGHT - 38))

    pygame.display.flip()

# ---------------- MAIN GAME LOOP ----------------

running = True

while running:

    clock.tick(60)

    # Check keyboard and mouse input.
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_r:
                mirrors = starting_mirrors.copy()

            elif event.key == pygame.K_SPACE:
                _, hit_target = trace_laser()
                if hit_target and level_index < len(levels) - 1:
                    level_index += 1
                    load_level(level_index)

        elif event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = event.pos

            # Convert mouse coordinates into grid coordinates.
            col = mouse_x // CELL
            row = (mouse_y - TOP) // CELL

            cell = (col, row)

            if event.button == 1 and cell in mirrors:
                dragging_mirror = cell
                dragging_mouse_pos = event.pos
            elif event.button == 3 and cell in mirrors:
                if mirrors[cell] == "/":
                    mirrors[cell] = "\\"
                else:
                    mirrors[cell] = "/"

        elif event.type == pygame.MOUSEMOTION and dragging_mirror is not None:
            dragging_mouse_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if dragging_mirror is not None:
                mouse_x, mouse_y = event.pos
                col = mouse_x // CELL
                row = (mouse_y - TOP) // CELL
                destination = (col, row)
                destination_is_on_board = (
                    0 <= col < COLS and 0 <= row < ROWS
                )

                if (
                    destination_is_on_board
                    and destination not in obstacles
                    and destination != source
                    and destination != target
                    and destination not in mirrors
                ):
                    mirrors[destination] = mirrors.pop(dragging_mirror)

                dragging_mirror = None
                dragging_mouse_pos = None

    draw_game()

pygame.quit()