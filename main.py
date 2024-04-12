import pygame
import random
import math

# Initialize the game

pygame.init()

FPS = 60

WIDTH, HEIGHT = 800, 800
ROWS = 4
COLS = 4

RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS

OUTLINE_COLOUR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOUR = (205, 192, 180)
FONT_COLOUR = (119, 110, 101)

# Fonts
FONT = pygame.font.SysFont("comicsans", 60, bold=True)
MOVE_VEL = 20  # Velocity of the movement of the tiles (in pixels per second)

GAME_WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")


# Game tile class
class Tile:
    COLORS = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = self.col * RECT_WIDTH
        self.y = self.row * RECT_HEIGHT

    def get_colour(self):
        color_index = int(math.log2(self.value)) - 1
        return self.COLORS[color_index]

    def draw(self, game_window):
        colour = self.get_colour()
        pygame.draw.rect(game_window, colour, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        text = FONT.render(str(self.value), 1, FONT_COLOUR)
        game_window.blit(
            text,
            (
                self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
                self.y + (RECT_HEIGHT / 2 - text.get_height() / 2)
            )
        )

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]
        # self.row = self.y // RECT_HEIGHT
        # self.col = self.x // RECT_WIDTH


def draw_grid(game_window):
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(game_window, OUTLINE_COLOUR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(game_window, OUTLINE_COLOUR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)

    pygame.draw.rect(game_window, OUTLINE_COLOUR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)


def draw(game_window, tiles):
    # Clear Screen and draw game grid and tiles
    game_window.fill(BACKGROUND_COLOUR)

    for tile in tiles.values():
        tile.draw(game_window)

    draw_grid(game_window)
    # Draw the tiles
    pygame.display.update()


def get_random_pos(tiles):
    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        if f"{row}{col}" not in tiles:
            break

    return row, col


def move_tiles(window, tiles, clock, direction):
    global merge_check, move_check, boundary_check, get_next_tile, delta
    updated = True
    blocks = set()

    if direction == 'left':
        sort_func = lambda x: x.col
        ascending_order = False
        delta = (-MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col - 1}", None)
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL
        move_check = lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL
        ceil = True  # ensure round up
    elif direction == "right":
        sort_func = lambda x: x.col
        ascending_order = True
        delta = (MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col + 1}", None)
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
        move_check = lambda tile, next_tile: tile.x < next_tile.x - RECT_WIDTH - MOVE_VEL
        ceil = False
    elif direction == "up":
        sort_func = lambda x: x.row
        ascending_order = False
        delta = (0, -MOVE_VEL)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}", None)
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        move_check = lambda tile, next_tile: tile.y > next_tile.y + RECT_HEIGHT + MOVE_VEL
        ceil = True
    elif direction == "down":
        sort_func = lambda x: x.row
        ascending_order = True
        delta = (0, MOVE_VEL)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}", None)
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
        move_check = lambda tile, next_tile: tile.y < next_tile.y - RECT_HEIGHT - MOVE_VEL
        ceil = False

    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=ascending_order)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif (
                tile.value == next_tile.value
                and tile not in blocks
                and next_tile not in blocks
            ):
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue

            tile.set_pos(ceil)
            updated = True

        update_tiles(window, tiles, sorted_tiles)
    end_move(tiles)


def end_move(tiles):
    if len(tiles) == 16:
        return "lost"

    row, col = get_random_pos(tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2, 4]), row, col)
    return "continue"


def update_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile

    draw(window, tiles)


def generate_tiles():
    tiles = {}
    for _ in range(2):
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)

    return tiles


def game_loop(game_window):
    clock = pygame.time.Clock()
    run = True

    tiles = generate_tiles()

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_tiles(game_window, tiles, clock, "left")
                elif event.key == pygame.K_RIGHT:
                    move_tiles(game_window, tiles, clock, "right")
                elif event.key == pygame.K_UP:
                    move_tiles(game_window, tiles, clock, "up")
                elif event.key == pygame.K_DOWN:
                    move_tiles(game_window, tiles, clock, "down")

        draw(game_window, tiles)
    pygame.quit()


if __name__ == "__main__":
    game_loop(GAME_WINDOW)
