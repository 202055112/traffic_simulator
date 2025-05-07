import pygame

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 40
ROWS = HEIGHT // GRID_SIZE
COLS = WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
ROAD_COLOR = (100, 100, 100)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Traffic Simulator - Grid Map")

# Clock
clock = pygame.time.Clock()

# Define road map (1 = road, 0 = empty)
# Vertical and horizontal cross roads example
road_map = [[0 for _ in range(COLS)] for _ in range(ROWS)]
for i in range(ROWS):
    road_map[i][5] = 1  # vertical road
for j in range(COLS):
    road_map[7][j] = 1  # horizontal road

# Draw grid lines and roads
def draw_grid():
    for i in range(ROWS):
        for j in range(COLS):
            rect = pygame.Rect(j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            if road_map[i][j] == 1:
                pygame.draw.rect(screen, ROAD_COLOR, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

# Main loop
running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_grid()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
