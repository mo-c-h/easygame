import pygame
import random

# Constants
SCREEN_WIDTH = 600  # 2 players, each 300 width
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
FPS = 10
MOVE_DELAY = 150  # Delay in milliseconds for movement
ROTATE_DELAY = 200  # Delay in milliseconds for rotation
GRAY = (128, 128, 128)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0)]

# Tetris Shapes
SHAPES = [
    [[1, 1, 1], [0, 1, 0]],  # T-shape
    [[1, 1, 1, 1]],  # I-shape
    [[1, 1], [1, 1]],  # O-shape
    [[0, 1, 1], [1, 1, 0]],  # Z-shape
    [[1, 1, 0], [0, 1, 1]],  # S-shape
    [[1, 1, 1], [1, 0, 0]],  # L-shape left
    [[1, 1, 1], [0, 0, 1]],  # L-shape right
]


class Tetris:
    def __init__(self, x_offset=0):
        self.x_offset = x_offset  # Offset for player 2
        self.grid_width = SCREEN_WIDTH // 2 // BLOCK_SIZE
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]
        self.current_shape = self.new_shape()
        self.speed = 300  # Faster falling speed
        self.last_fall_time = pygame.time.get_ticks()
        self.last_move_time = pygame.time.get_ticks()  # Last move left/right
        self.last_rotate_time = pygame.time.get_ticks()  # Last rotate
        self.move_delay = MOVE_DELAY
        self.rotate_delay = ROTATE_DELAY
        self.game_over = False  # Game over flag

    def new_shape(self):
        shape = random.choice(SHAPES)
        color = random.choice(COLORS)
        return {'shape': shape, 'color': color, 'pos': [0, self.grid_width // 2 - len(shape[0]) // 2]}

    def draw_grid(self, screen):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x]:
                    pygame.draw.rect(screen, self.grid[y][x],
                                     (self.x_offset + x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def draw_shape(self, screen):
        shape = self.current_shape['shape']
        color = self.current_shape['color']
        pos = self.current_shape['pos']
        for y in range(len(shape)):
            for x in range(len(shape[y])):
                if shape[y][x]:
                    pygame.draw.rect(screen, color, (
                    self.x_offset + (pos[1] + x) * BLOCK_SIZE, (pos[0] + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def check_collision(self, offset):
        shape = self.current_shape['shape']
        pos = self.current_shape['pos']
        for y in range(len(shape)):
            for x in range(len(shape[y])):
                if shape[y][x]:
                    new_x = pos[1] + x + offset[1]
                    new_y = pos[0] + y + offset[0]
                    if new_x < 0 or new_x >= self.grid_width or new_y >= SCREEN_HEIGHT // BLOCK_SIZE or (
                            new_y >= 0 and self.grid[new_y][new_x]):
                        return True
        return False

    def merge_shape(self):
        shape = self.current_shape['shape']
        pos = self.current_shape['pos']
        for y in range(len(shape)):
            for x in range(len(shape[y])):
                if shape[y][x]:
                    self.grid[pos[0] + y][pos[1] + x] = self.current_shape['color']

    def clear_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(row)]
        for i in lines_to_clear:
            del self.grid[i]
            self.grid.insert(0, [0 for _ in range(self.grid_width)])
        return len(lines_to_clear)

    def add_garbage_lines(self, count):
        for _ in range(count):
            empty_spot = random.randint(0, self.grid_width - 1)  # Random empty spot
            new_line = [GRAY if i != empty_spot else 0 for i in range(self.grid_width)]
            self.grid.append(new_line)
            del self.grid[0]  # Remove the top line to make space for the new garbage line

    def rotate_shape(self, clockwise=True):
        original_shape = self.current_shape['shape']
        if clockwise:
            self.current_shape['shape'] = [list(row) for row in zip(*original_shape[::-1])]
        else:
            self.current_shape['shape'] = [list(row)[::-1] for row in zip(*original_shape)]
        if self.check_collision((0, 0)):
            self.current_shape['shape'] = original_shape

    def is_game_over(self):
        # Game over if any block is present in the top row
        return any(self.grid[0])

    def run(self, keys, control_scheme):
        if self.game_over:
            return 0  # No actions if game is over

        current_time = pygame.time.get_ticks()

        # Movement and rotation based on control scheme
        left, right, down, rotate = control_scheme

        # Move left/right with delay
        if current_time - self.last_move_time > self.move_delay:
            if keys[left] and not self.check_collision((0, -1)):
                self.current_shape['pos'][1] -= 1
                self.last_move_time = current_time
            if keys[right] and not self.check_collision((0, 1)):
                self.current_shape['pos'][1] += 1
                self.last_move_time = current_time

        # Move down continuously without delay
        if keys[down] and not self.check_collision((1, 0)):
            self.current_shape['pos'][0] += 1

        # Rotate with delay
        if current_time - self.last_rotate_time > self.rotate_delay:
            if keys[rotate]:
                self.rotate_shape(clockwise=True)
                self.last_rotate_time = current_time

        # Automatic falling
        if pygame.time.get_ticks() - self.last_fall_time > self.speed:
            if not self.check_collision((1, 0)):
                self.current_shape['pos'][0] += 1
            else:
                self.merge_shape()
                cleared_lines = self.clear_lines()
                self.current_shape = self.new_shape()
                if self.is_game_over():
                    self.game_over = True  # Mark the game as over if the new shape overlaps with blocks
                    return -1  # Return -1 to signal game over
                return cleared_lines
            self.last_fall_time = pygame.time.get_ticks()
        return 0


def display_text(screen, text, x, y, font_size=50, color=WHITE):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    player1 = Tetris(x_offset=0)
    player2 = Tetris(x_offset=SCREEN_WIDTH // 2)

    running = True
    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()

        # Player 1 controls: A, D, S, W for left, right, down, and rotate (right rotation)
        player1_controls = [pygame.K_a, pygame.K_d, pygame.K_s, pygame.K_w]
        lines_cleared_p1 = player1.run(keys, player1_controls)

        # Player 2 controls: Arrow keys for left, right, down, and rotate (right rotation)
        player2_controls = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_UP]
        lines_cleared_p2 = player2.run(keys, player2_controls)

        # If player1 clears lines, add garbage to player2
        if lines_cleared_p1 > 0:
            player2.add_garbage_lines(lines_cleared_p1)

        # If player2 clears lines, add garbage to player1
        if lines_cleared_p2 > 0:
            player1.add_garbage_lines(lines_cleared_p2)

        # Check for game over
        if player1.game_over:
            display_text(screen, "LOSE", 50, SCREEN_HEIGHT // 2)
            display_text(screen, "WIN", SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2)
        elif player2.game_over:
            display_text(screen, "WIN", 50, SCREEN_HEIGHT // 2)
            display_text(screen, "LOSE", SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2)
        else:
            # Draw both players' grids and shapes
            player1.draw_grid(screen)
            player1.draw_shape(screen)

            player2.draw_grid(screen)
            player2.draw_shape(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
