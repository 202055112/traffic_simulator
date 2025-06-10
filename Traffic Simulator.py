import pygame
import sys
import random
import time

# 화면 설정
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 40
ROWS = HEIGHT // GRID_SIZE
COLS = WIDTH // GRID_SIZE

# 색상 정의
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
ROAD_COLOR = (100, 100, 100)
CAR_COLOR = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 초기화
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Simulator")
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

# 게임 상태
# 메뉴, 입력, 게임플레이 등의 상태를 구분
# 충돌 여부, 교차로 및 차량 리스트, 사용자 입력 등을 정의 
game_state = "menu"
car_crashed = False
intersections = []
cars = []
road_map = [[0 for _ in range(COLS)] for _ in range(ROWS)]
crash_enabled = False  # 시작 시 충돌 감지 꺼짐
spawn_timer = 0
spawn_interval = 60
paused = False
user_input = ""

# 버튼 클래스 정의
class Button:
    def __init__(self, text, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect)
        txt = font.render(self.text, True, BLACK)
        screen.blit(txt, (self.rect.x + 10, self.rect.y + 10))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# 신호등 클래스 정의
class TrafficLight:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.states = {'horizontal': 'green', 'vertical': 'red'}
        self.timer = 0
        self.interval = 180  # 신호 전환 주기

    def update(self):
        self.timer += 1
        if self.timer > self.interval:
            self.timer = 0
            # 수평 ↔ 수직 신호 전환
            self.states['horizontal'], self.states['vertical'] = self.states['vertical'], self.states['horizontal']

    def get_state(self, direction):
        return self.states['horizontal'] if direction in ["left", "right"] else self.states['vertical']

    def draw(self):
        # 수평, 수직 신호등 각각 표시
        color_h = GREEN if self.states['horizontal'] == 'green' else RED
        color_v = GREEN if self.states['vertical'] == 'green' else RED
        pygame.draw.circle(screen, color_h, (self.x - 10, self.y), 6)
        pygame.draw.circle(screen, color_v, (self.x + 10, self.y), 6)

# 교차로 클래스 정의
class Intersection:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = col * GRID_SIZE + GRID_SIZE // 2
        self.y = row * GRID_SIZE + GRID_SIZE // 2
        self.light = TrafficLight(self.x, self.y)

    def update(self):
        self.light.update()

    def draw(self):
        self.light.draw()
        pygame.draw.rect(screen, BLACK, (self.col * GRID_SIZE, self.row * GRID_SIZE, GRID_SIZE, GRID_SIZE), 2)

    def get_light_state(self, direction):
        return self.light.get_state(direction)

# 차량 클래스 정의
class Car:
    def __init__(self, row, col, direction):
        self.row = row
        self.col = col
        self.direction = direction
        offset = 6 if direction in ["left", "up"] else 18
        self.x = col * GRID_SIZE + offset
        self.y = row * GRID_SIZE + offset
        self.width = 10
        self.height = 10
        self.speed = 1
        self.waiting = False

    def is_too_close(self, other):
        # 같은 방향, 너무 가까운 차량 판단
        if self.direction != other.direction:
            return False
        if self.direction == "right" and other.x > self.x and abs(self.y - other.y) < self.height and (other.x - self.x) < 20:
            return True
        if self.direction == "left" and other.x < self.x and abs(self.y - other.y) < self.height and (self.x - other.x) < 20:
            return True
        if self.direction == "down" and other.y > self.y and abs(self.x - other.x) < self.width and (other.y - self.y) < 20:
            return True
        if self.direction == "up" and other.y < self.y and abs(self.x - other.x) < self.width and (self.y - other.y) < 20:
            return True
        return False

    def move(self):
        # 교차로 + 빨간불이면 정지
        if self.at_intersection() and self.get_light_state() == "red":
            self.waiting = True
            return

        # 충돌 방지 활성화 상태면 거리 유지
        if not crash_enabled:
            for other in cars:
                if other is not self and self.is_too_close(other):
                    self.waiting = True
                    return

        # 이동
        self.waiting = False
        if self.direction == "right": self.x += self.speed
        elif self.direction == "left": self.x -= self.speed
        elif self.direction == "down": self.y += self.speed
        elif self.direction == "up": self.y -= self.speed

    def draw(self):
        if 0 <= self.x < WIDTH and 0 <= self.y < HEIGHT:
            pygame.draw.rect(screen, CAR_COLOR, (self.x, self.y, self.width, self.height))

    def is_off_screen(self):
        return not (0 <= self.x < WIDTH and 0 <= self.y < HEIGHT)

    def at_intersection(self):
        return any(abs(self.x - i.x) < GRID_SIZE // 2 and abs(self.y - i.y) < GRID_SIZE // 2 for i in intersections)

    def get_light_state(self):
        for i in intersections:
            if abs(self.x - i.x) < GRID_SIZE // 2 and abs(self.y - i.y) < GRID_SIZE // 2:
                return i.get_light_state(self.direction)
        return "green"

# 격자 및 도로 표시

def draw_grid():
    for i in range(ROWS):
        for j in range(COLS):
            color = ROAD_COLOR if road_map[i][j] == 1 else WHITE
            pygame.draw.rect(screen, color, (j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, GRAY, (j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

# 교차로 자동 생성 (랜덤 위치)
def generate_intersections(n):
    global intersections, road_map
    intersections.clear()
    road_map = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    count = 0
    while count < n:
        row = random.randint(2, ROWS - 3)
        col = random.randint(2, COLS - 3)
        if all(abs(i.row - row) > 1 or abs(i.col - col) > 1 for i in intersections):
            intersections.append(Intersection(row, col))
            for i in range(ROWS): road_map[i][col] = 1
            for j in range(COLS): road_map[row][j] = 1
            count += 1

# 차량 생성

def spawn_car():
    direction = random.choice(["up", "down", "left", "right"])
    if direction == "right":
        row = random.choice([i for i in range(ROWS) if road_map[i][0] == 1])
        return Car(row, 0, direction)
    elif direction == "left":
        row = random.choice([i for i in range(ROWS) if road_map[i][COLS - 1] == 1])
        return Car(row, COLS - 1, direction)
    elif direction == "down":
        col = random.choice([j for j in range(COLS) if road_map[0][j] == 1])
        return Car(0, col, direction)
    elif direction == "up":
        col = random.choice([j for j in range(COLS) if road_map[ROWS - 1][j] == 1])
        return Car(ROWS - 1, col, direction)

# 게임 초기화

def reset_game():
    global cars, car_crashed
    cars.clear()
    car_crashed = False

# 중앙 텍스트 표시

def draw_text_center(text, y_offset=0):
    txt = font.render(text, True, RED)
    screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - txt.get_height() // 2 + y_offset))

# UI 버튼 및 입력 상자
start_button = Button("Start", WIDTH // 2 - 50, HEIGHT // 2 + 40, 100, 50)
input_box = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 100, 100, 40)

# 메인 루프
while True:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.is_clicked(event.pos):
                game_state = "input"
        elif game_state == "input" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if user_input.isdigit() and 1 <= int(user_input) <= 10:
                    generate_intersections(int(user_input))
                    reset_game()
                    game_state = "play"
                    user_input = ""
            elif event.key == pygame.K_BACKSPACE:
                user_input = user_input[:-1]
            else:
                if len(user_input) < 2 and event.unicode.isdigit():
                    user_input += event.unicode
        elif game_state == "play" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                crash_enabled = not crash_enabled
                if not crash_enabled:
                    car_crashed = False
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_ESCAPE:
                game_state = "menu"
                cars.clear()
                intersections.clear()

    # 상태별 렌더링
    if game_state == "menu":
        draw_text_center("Traffic Simulator")
        start_button.draw()

    elif game_state == "input":
        draw_text_center("Enter number of intersections (1-10):")
        pygame.draw.rect(screen, WHITE, input_box)
        pygame.draw.rect(screen, BLACK, input_box, 2)
        txt_surface = font.render(user_input, True, BLACK)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

    elif game_state == "play":
        draw_grid()
        for i in intersections:
            i.update()
            i.draw()

        if not paused and not car_crashed:
            spawn_timer += 1
            if spawn_timer > spawn_interval:
                spawn_timer = 0
                new_car = spawn_car()
                if new_car:
                    cars.append(new_car)

            for car in cars:
                car.move()

            if crash_enabled:
                for i1 in range(len(cars)):
                    for i2 in range(i1 + 1, len(cars)):
                        c1, c2 = cars[i1], cars[i2]
                        rect1 = pygame.Rect(c1.x, c1.y, c1.width, c1.height)
                        rect2 = pygame.Rect(c2.x, c2.y, c2.width, c2.height)
                        if rect1.colliderect(rect2):
                            car_crashed = True
                            paused = True

            cars = [c for c in cars if not c.is_off_screen()]

        for car in cars:
            car.draw()

        if car_crashed:
            draw_text_center("Car Crashed!", 50)

        status_text = "Collision Detection: ON" if crash_enabled else "Collision Detection: OFF"
        status_surf = font.render(status_text, True, RED if crash_enabled else GREEN)
        screen.blit(status_surf, (10, 10))

        if paused:
            draw_text_center("Paused", 100)

    pygame.display.flip()
    clock.tick(60)
