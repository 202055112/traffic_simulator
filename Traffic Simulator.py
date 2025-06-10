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
game_state = "menu"
car_crashed = False
intersections = []
cars = []
road_map = [[0 for _ in range(COLS)] for _ in range(ROWS)]
crash_enabled = False
spawn_timer = 0
spawn_interval = 60
paused = False
user_input = ""

# 버튼 클래스
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

# 신호등 클래스
class TrafficLight:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.states = {'horizontal': 'green', 'vertical': 'red'}
        self.timer = 0
        self.interval = 180

    def update(self):
        self.timer += 1
        if self.timer > self.interval:
            self.timer = 0
            self.states['horizontal'], self.states['vertical'] = (
                self.states['vertical'], self.states['horizontal']
            )

    def get_state(self, direction):
        return self.states['horizontal'] if direction in ["left", "right"] else self.states['vertical']

    def will_soon_turn_red(self, direction, threshold=30):
        if self.get_state(direction) == 'green':
            return self.timer > self.interval - threshold
        return False

    def draw(self):
        color_h = GREEN if self.states['horizontal'] == 'green' else RED
        color_v = GREEN if self.states['vertical'] == 'green' else RED
        pygame.draw.circle(screen, color_h, (self.x - 10, self.y), 6)
        pygame.draw.circle(screen, color_v, (self.x + 10, self.y), 6)

# 교차로 클래스
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

# 차량 클래스
class Car:
    def __init__(self, row, col, direction):
        self.direction = direction
        offset = 6 if direction in ["left", "up"] else 18
        self.x = col * GRID_SIZE + offset
        self.y = row * GRID_SIZE + offset
        self.width = 10
        self.height = 10
        self.speed = 1
        self.waiting = False

    def is_too_close(self, other):
        if self.direction != other.direction:
            return False
        if self.direction == "right" and other.x > self.x and abs(self.y - other.y) < self.height and other.x - self.x < 20:
            return True
        if self.direction == "left" and other.x < self.x and abs(self.y - other.y) < self.height and self.x - other.x < 20:
            return True
        if self.direction == "down" and other.y > self.y and abs(self.x - other.x) < self.width and other.y - self.y < 20:
            return True
        if self.direction == "up" and other.y < self.y and abs(self.x - other.x) < self.width and self.y - other.y < 20:
            return True
        return False

    def in_center(self, inter):
        return abs(self.x - inter.x) < self.width and abs(self.y - inter.y) < self.height

    def move(self):
        for inter in intersections:
            dist_x = abs(self.x - inter.x)
            dist_y = abs(self.y - inter.y)
            if dist_x < GRID_SIZE and dist_y < GRID_SIZE:
                state = inter.get_light_state(self.direction)
                soon_red = inter.light.will_soon_turn_red(self.direction)
                if state == 'red' or (soon_red and not self.in_center(inter)):
                    self.waiting = True
                    return

        if not crash_enabled:
            for other in cars:
                if other is not self and self.is_too_close(other):
                    self.waiting = True
                    return

        self.waiting = False
        if self.direction == "right": self.x += self.speed
        if self.direction == "left":  self.x -= self.speed
        if self.direction == "down":  self.y += self.speed
        if self.direction == "up":    self.y -= self.speed

    def draw(self):
        if 0 <= self.x < WIDTH and 0 <= self.y < HEIGHT:
            pygame.draw.rect(screen, CAR_COLOR, (self.x, self.y, self.width, self.height))

    def is_off_screen(self):
        return not (0 <= self.x < WIDTH and 0 <= self.y < HEIGHT)

# 격자 & 도로
def draw_grid():
    for i in range(ROWS):
        for j in range(COLS):
            color = ROAD_COLOR if road_map[i][j] == 1 else WHITE
            pygame.draw.rect(screen, color, (j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, GRAY, (j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

# 교차로 생성
def generate_intersections(n):
    global intersections, road_map
    intersections.clear()
    road_map = [[0]*COLS for _ in range(ROWS)]
    used_rows = set()
    used_cols = set()
    count = 0
    attempts = 0

    while count < n and attempts < 100:
        row = random.randint(2, ROWS-3)
        col = random.randint(2, COLS-3)
        if row in used_rows or col in used_cols:
            attempts += 1
            continue
        intersections.append(Intersection(row, col))
        used_rows.add(row)
        used_cols.add(col)
        for r in range(ROWS): road_map[r][col] = 1
        for c in range(COLS): road_map[row][c] = 1
        count += 1

    # 이제 도로끼리 교차하는 모든 위치에 신호등 추가
    extra = []
    for r in range(ROWS):
        for c in range(COLS):
            if road_map[r][c] == 1:
                horizontal = road_map[r]
                vertical = [road_map[x][c] for x in range(ROWS)]
                if any(horizontal) and any(vertical):
                    extra.append((r, c))

    intersections.clear()
    for (r, c) in extra:
        intersections.append(Intersection(r, c))

# 차량 생성
def spawn_car():
    direction = random.choice(["up","down","left","right"])
    if direction == "right":
        rows = [i for i in range(ROWS) if road_map[i][0] == 1]
        return Car(random.choice(rows), 0, direction)
    if direction == "left":
        rows = [i for i in range(ROWS) if road_map[i][COLS-1] == 1]
        return Car(random.choice(rows), COLS-1, direction)
    if direction == "down":
        cols = [j for j in range(COLS) if road_map[0][j] == 1]
        return Car(0, random.choice(cols), direction)
    if direction == "up":
        cols = [j for j in range(COLS) if road_map[ROWS-1][j] == 1]
        return Car(ROWS-1, random.choice(cols), direction)

def reset_game():
    global cars, car_crashed
    cars.clear()
    car_crashed = False

def draw_text_center(text, y_offset=0):
    txt = font.render(text, True, RED)
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - txt.get_height()//2 + y_offset))

start_button = Button("Start", WIDTH//2 - 50, HEIGHT//2 + 40, 100, 50)
input_box = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 100, 100, 40)

# 메인 루프
while True:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_state=="menu" and event.type==pygame.MOUSEBUTTONDOWN:
            if start_button.is_clicked(event.pos):
                game_state="input"
        elif game_state=="input" and event.type==pygame.KEYDOWN:
            if event.key==pygame.K_RETURN and user_input.isdigit() and 1<=int(user_input)<=10:
                generate_intersections(int(user_input))
                reset_game()
                game_state="play"
                user_input=""
            elif event.key==pygame.K_BACKSPACE:
                user_input=user_input[:-1]
            elif event.unicode.isdigit() and len(user_input)<2:
                user_input += event.unicode
        elif game_state=="play" and event.type==pygame.KEYDOWN:
            if event.key==pygame.K_p:
                crash_enabled = not crash_enabled
                if not crash_enabled: car_crashed=False
            if event.key==pygame.K_SPACE:
                paused = not paused
            if event.key==pygame.K_ESCAPE:
                game_state="menu"
                cars.clear()
                intersections.clear()

    if game_state=="menu":
        draw_text_center("Traffic Simulator")
        start_button.draw()
    elif game_state=="input":
        draw_text_center("Enter number of intersections (1-10):")
        pygame.draw.rect(screen, WHITE, input_box)
        pygame.draw.rect(screen, BLACK, input_box, 2)
        screen.blit(font.render(user_input, True, BLACK), (input_box.x+5, input_box.y+5))
    else:
        draw_grid()
        for inter in intersections:
            inter.update()
            inter.draw()

        if not paused and not car_crashed:
            spawn_timer += 1
            if spawn_timer > spawn_interval:
                spawn_timer = 0
                car = spawn_car()
                if car: cars.append(car)

            for car in cars:
                car.move()

            if crash_enabled:
                for i in range(len(cars)):
                    for j in range(i+1, len(cars)):
                        if pygame.Rect(cars[i].x,cars[i].y,cars[i].width,cars[i].height).colliderect(
                           pygame.Rect(cars[j].x,cars[j].y,cars[j].width,cars[j].height)):
                            car_crashed = True
                            paused = True

            cars = [c for c in cars if not c.is_off_screen()]

        for car in cars: car.draw()

        if car_crashed:
            draw_text_center("Car Crashed!", 50)

        status = "Collision Detection: ON" if crash_enabled else "Collision Detection: OFF"
        color = RED if crash_enabled else GREEN
        screen.blit(font.render(status, True, color), (10,10))
        if paused:
            draw_text_center("Paused", 100)

    pygame.display.flip()
    clock.tick(60)
