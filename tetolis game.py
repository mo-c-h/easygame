import pygame
import random

# Constants
SCREEN_WIDTH = 300  # Reduced width
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
FPS = 60
SPEED_INCREASE = 100  # Increase sensitivity in milliseconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0)]

# Tetris Shapes
SHAPES = [
    [[1, 1, 1], [0, 1, 0]],  # T-shape
    [[1, 1, 1, 1]],          # I-shape
    [[1, 1], [1, 1]],        # O-shape
    [[0, 1, 1], [1, 1, 0]],  # Z-shape
    [[1, 1, 0], [0, 1, 1]],  # S-shape
]

class Tetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.grid = [[0 for _ in range(SCREEN_WIDTH // BLOCK_SIZE)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]
        self.current_shape = self.new_shape()
        self.speed = 300  # Faster falling speed
        self.last_fall_time = pygame.time.get_ticks()

    def new_shape(self):
        shape = random.choice(SHAPES)
        color = random.choice(COLORS)
        return {'shape': shape, 'color': color, 'pos': [0, (SCREEN_WIDTH // BLOCK_SIZE) // 2 - len(shape[0]) // 2]}

    def draw_grid(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen, self.grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def draw_shape(self):
        shape = self.current_shape['shape']
        color = self.current_shape['color']
        pos = self.current_shape['pos']
        for y in range(len(shape)):
            for x in range(len(shape[y])):
                if shape[y][x]:
                    pygame.draw.rect(self.screen, color, ((pos[1] + x) * BLOCK_SIZE, (pos[0] + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def check_collision(self, offset):
        shape = self.current_shape['shape']
        pos = self.current_shape['pos']
        for y in range(len(shape)):
            for x in range(len(shape[y])):
                if shape[y][x]:
                    new_x = pos[1] + x + offset[1]
                    new_y = pos[0] + y + offset[0]
                    if new_x < 0 or new_x >= SCREEN_WIDTH // BLOCK_SIZE or new_y >= SCREEN_HEIGHT // BLOCK_SIZE or (new_y >= 0 and self.grid[new_y][new_x]):
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
            self.grid.insert(0, [0 for _ in range(SCREEN_WIDTH // BLOCK_SIZE)])

    def run(self):
        running = True
        while running:
            self.screen.fill(BLACK)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False  # Exit on ESC key

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and not self.check_collision((0, -1)):
                self.current_shape['pos'][1] -= 1
            if keys[pygame.K_RIGHT] and not self.check_collision((0, 1)):
                self.current_shape['pos'][1] += 1
            if keys[pygame.K_DOWN] and not self.check_collision((1, 0)):
                self.current_shape['pos'][0] += 1
            if keys[pygame.K_UP]:  # Rotate shape
                original_shape = self.current_shape['shape']
                self.current_shape['shape'] = [list(row) for row in zip(*self.current_shape['shape'][::-1])]
                if self.check_collision((0, 0)):
                    self.current_shape['shape'] = original_shape  # Undo rotation

            # Automatic falling
            if pygame.time.get_ticks() - self.last_fall_time > self.speed:
                if not self.check_collision((1, 0)):
                    self.current_shape['pos'][0] += 1
                else:
                    self.merge_shape()
                    self.clear_lines()
                    self.current_shape = self.new_shape()
                self.last_fall_time = pygame.time.get_ticks()

            self.draw_grid()
            self.draw_shape()
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Tetris()
    game.run()
    pygame.quit()
