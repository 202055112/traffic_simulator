import pygame
import random

# 초기화
pygame.init()

# 상수 설정
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 40
ROWS = HEIGHT // GRID_SIZE
COLS = WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
ROAD_COLOR = (100, 100, 100)
CAR_COLOR = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 디스플레이 설정
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Traffic Simulator")
clock = pygame.time.Clock()

# 도로 지도 설정
road_map = [[0 for _ in range(COLS)] for _ in range(ROWS)]
for i in range(ROWS):
    road_map[i][5] = 1
for j in range(COLS):
    road_map[7][j] = 1

# 클래스 정의
class Car:
    def __init__(self, x, y, direction="right"):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 2
        self.width = GRID_SIZE // 2
        self.height = GRID_SIZE // 2

    def update(self, intersections, other_cars):
        # 충돌 방지
        for other in other_cars:
            if other != self and self.check_collision(other):
                return  # 충돌이 예상되면 멈춤

        for inter in intersections:
            lx, ly = inter.col * GRID_SIZE + GRID_SIZE // 2, inter.row * GRID_SIZE + GRID_SIZE // 2
            if self.direction == "right":
                if abs(self.x + self.width - lx) < 5 and abs(self.y - ly) < GRID_SIZE // 2:
                    if inter.traffic_light.state == "red":
                        return
            elif self.direction == "down":
                if abs(self.y + self.height - ly) < 5 and abs(self.x - lx) < GRID_SIZE // 2:
                    if inter.traffic_light.state == "red":
                        return

        # 이동
        if self.direction == "right":
            self.x += self.speed
        elif self.direction == "down":
            self.y += self.speed

    def check_collision(self, other):
        return pygame.Rect(self.x, self.y, self.width, self.height).colliderect(
               pygame.Rect(other.x, other.y, other.width, other.height))

    def draw(self, surface):
        pygame.draw.rect(surface, CAR_COLOR, (self.x, self.y, self.width, self.height))


class TrafficLight:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = "green"
        self.timer = 0
        self.change_interval = 180  # 3초

    def update(self):
        self.timer += 1
        if self.timer >= self.change_interval:
            self.timer = 0
            self.state = "red" if self.state == "green" else "green"

    def draw(self, surface):
        color = GREEN if self.state == "green" else RED
        pygame.draw.circle(surface, color, (self.x, self.y), 10)
        # 타이머 숫자 시각화
        font = pygame.font.SysFont(None, 24)
        remaining = (self.change_interval - self.timer) // 60 + 1
        text = font.render(str(remaining), True, BLACK)
        surface.blit(text, (self.x + 12, self.y - 12))


class Intersection:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.traffic_light = TrafficLight(col * GRID_SIZE + GRID_SIZE // 2, row * GRID_SIZE + GRID_SIZE // 2)

    def update(self):
        self.traffic_light.update()

    def draw(self, surface):
        self.traffic_light.draw(surface)

# 차량 리스트 및 교차로 생성
cars = []
intersections = [Intersection(7, 5)]

# 격자 및 도로 그리기
def draw_grid():
    for i in range(ROWS):
        for j in range(COLS):
            rect = pygame.Rect(j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            if road_map[i][j] == 1:
                pygame.draw.rect(screen, ROAD_COLOR, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

# 차량 생성 함수
def spawn_car():
    direction = random.choice(["right", "down"])
    if direction == "right":
        return Car(0, 7 * GRID_SIZE + 10, "right")
    else:
        return Car(5 * GRID_SIZE + 10, 0, "down")

# 시뮬레이션 변수
simulation_running = True
car_spawn_timer = 0
car_spawn_interval = 180  # 3초

# 메인 루프
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            simulation_running = not simulation_running

    draw_grid()

    if simulation_running:
        # 신호등 업데이트
        for inter in intersections:
            inter.update()
            inter.draw(screen)

        # 차량 업데이트
        for car in cars:
            car.update(intersections, cars)
            car.draw(screen)

        # 차량 자동 생성
        car_spawn_timer += 1
        if car_spawn_timer >= car_spawn_interval:
            cars.append(spawn_car())
            car_spawn_timer = 0
    else:
        for inter in intersections:
            inter.draw(screen)
        for car in cars:
            car.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
