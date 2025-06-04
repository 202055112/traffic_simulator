import pygame
import sys
import random

# 화면 크기 및 그리드 설정
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 40
ROWS = HEIGHT // GRID_SIZE  # 세로 그리드 개수
COLS = WIDTH // GRID_SIZE   # 가로 그리드 개수

# 색상 정의
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
ROAD_COLOR = (100, 100, 100)
CAR_COLOR = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Simulator")
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

# 게임 상태 및 변수 초기화
game_state = "menu"        # 현재 게임 상태 (메뉴, 입력, 플레이, 충돌 등)
car_crashed = False        # 충돌 발생 여부
intersections = []         # 교차로 리스트
cars = []                  # 차량 리스트
road_map = [[0 for _ in range(COLS)] for _ in range(ROWS)]  # 도로 여부 저장 2D 리스트
crash_enabled = False      # 충돌 감지 토글 변수 (True면 충돌 무시)
spawn_timer = 0            # 차량 생성 타이머
spawn_interval = 60        # 차량 생성 간격 (프레임 단위)
paused = False             # 일시정지 상태 여부
user_input = ""            # 사용자 입력 문자열

# 버튼 클래스 - UI 버튼 구현용
class Button:
    def __init__(self, text, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)  # 버튼 영역
        self.text = text

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect)
        txt = font.render(self.text, True, BLACK)
        screen.blit(txt, (self.rect.x + 10, self.rect.y + 10))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)  # 마우스 클릭이 버튼 안인지 판단

# 신호등 클래스
class TrafficLight:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.states = {'horizontal': 'green', 'vertical': 'red'}  # 초기 신호등 상태
        self.timer = 0
        self.interval = 180  # 신호 변경 간격(프레임)

    def update(self):
        self.timer += 1
        if self.timer > self.interval:
            self.timer = 0
            # 신호 바꾸기 (수평-수직 신호 스위칭)
            self.states['horizontal'], self.states['vertical'] = self.states['vertical'], self.states['horizontal']

    def get_state(self, direction):
        # 차량 진행 방향에 따라 신호 상태 반환
        return self.states['horizontal'] if direction in ["left", "right"] else self.states['vertical']

    def draw(self):
        # 신호등 색깔 표시
        color_h = GREEN if self.states['horizontal'] == 'green' else RED
        color_v = GREEN if self.states['vertical'] == 'green' else RED
        pygame.draw.circle(screen, color_h, (self.x - 10, self.y), 6)  # 좌측(수평)
        pygame.draw.circle(screen, color_v, (self.x + 10, self.y), 6)  # 우측(수직)

# 교차로 클래스
class Intersection:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = col * GRID_SIZE + GRID_SIZE // 2  # 화면 좌표 x
        self.y = row * GRID_SIZE + GRID_SIZE // 2  # 화면 좌표 y
        self.light = TrafficLight(self.x, self.y)  # 교차로 신호등 생성

    def update(self):
        self.light.update()  # 신호등 상태 업데이트

    def draw(self):
        self.light.draw()  # 신호등 그리기
        pygame.draw.rect(screen, BLACK, (self.col * GRID_SIZE, self.row * GRID_SIZE, GRID_SIZE, GRID_SIZE), 2)  # 교차로 테두리

    def get_light_state(self, direction):
        # 특정 방향의 신호등 상태 반환
        return self.light.get_state(direction)

# 자동차 클래스
class Car:
    def __init__(self, row, col, direction):
        self.row = row
        self.col = col
        self.direction = direction
        offset = 6 if direction in ["left", "up"] else 18  # 차량 좌표 조정 (좌/상은 약간 왼쪽 위에 붙음)
        self.x = col * GRID_SIZE + offset
        self.y = row * GRID_SIZE + offset
        self.width = 10
        self.height = 10
        self.speed = 1
        self.waiting = False  # 신호 대기 중인지

    def is_too_close(self, other):
        # 같은 방향 차량끼리 너무 가까운지 판단 (차량 간 최소 거리 유지)
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
        # 교차로 앞 신호가 빨간불이면 대기
        if self.at_intersection() and self.get_light_state() == "red":
            self.waiting = True
            return
        # 충돌 방지 기능이 켜져 있으면 앞 차량과 너무 가까우면 대기
        if not crash_enabled:
            for other in cars:
                if other is not self and self.is_too_close(other):
                    self.waiting = True
                    return
        self.waiting = False
        # 방향에 따라 차량 이동
        if self.direction == "right": self.x += self.speed
        elif self.direction == "left": self.x -= self.speed
        elif self.direction == "down": self.y += self.speed
        elif self.direction == "up": self.y -= self.speed

    def draw(self):
        # 화면 내에 있을 때만 차량 그리기
        if 0 <= self.x < WIDTH and 0 <= self.y < HEIGHT:
            pygame.draw.rect(screen, CAR_COLOR, (self.x, self.y, self.width, self.height))

    def is_off_screen(self):
        # 화면 밖으로 나갔는지 체크
        return not (0 <= self.x < WIDTH and 0 <= self.y < HEIGHT)

    def at_intersection(self):
        # 차량이 교차로 범위 안에 있는지 체크
        for i in intersections:
            if abs(self.x - i.x) < GRID_SIZE // 2 and abs(self.y - i.y) < GRID_SIZE // 2:
                return True
        return False

    def get_light_state(self):
        # 차량 현재 위치에 맞는 교차로 신호 상태 반환
        for i in intersections:
            if abs(self.x - i.x) < GRID_SIZE // 2 and abs(self.y - i.y) < GRID_SIZE // 2:
                return i.get_light_state(self.direction)
        return "green"  # 교차로 근처가 아니면 초록불로 간주

# 그리드 및 도로 그리기 함수
def draw_grid():
    for i in range(ROWS):
        for j in range(COLS):
            color = ROAD_COLOR if road_map[i][j] == 1 else WHITE  # 도로 여부에 따라 색상 결정
            pygame.draw.rect(screen, color, (j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, GRAY, (j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)  # 그리드 선

# 교차로 생성 함수 (랜덤 위치 n개 생성 및 도로 맵 업데이트)
def generate_intersections(n):
    global intersections, road_map
    intersections.clear()
    road_map = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    for _ in range(n):
        row = random.randint(2, ROWS - 3)
        col = random.randint(2, COLS - 3)
        intersections.append(Intersection(row, col))
        # 해당 열과 행에 도로 표시
        for i in range(ROWS): road_map[i][col] = 1
        for j in range(COLS): road_map[row][j] = 1

# 차량 생성 함수 (랜덤 방향, 도로 가장자리에서 생성)
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

# 게임 초기화 함수 (차량 초기화 및 충돌 상태 초기화)
def reset_game():
    global cars, car_crashed
    cars.clear()
    car_crashed = False

# 화면 중앙에 텍스트 출력 함수
def draw_text_center(text, y_offset=0):
    txt = font.render(text, True, RED)
    screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - txt.get_height() // 2 + y_offset))

# 시작 버튼 생성
start_button = Button("Start", WIDTH // 2 - 50, HEIGHT // 2 + 40, 100, 50)
# 사용자 입력 박스 생성
input_box = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 100, 100, 40)

# 메인 루프 시작
while True:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # 메뉴 상태에서 시작 버튼 클릭 시 입력 상태로 전환
        if game_state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.is_clicked(event.pos):
                game_state = "input"
        # 입력 상태에서 키보드 입력 처리
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
        # 플레이 상태 키 입력
        elif game_state == "play" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                # p 키 눌러 충돌 토글 및 충돌 발생 표시
                crash_enabled = not crash_enabled
                if not crash_enabled:
                    car_crashed = False
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_ESCAPE:
                game_state = "menu"
                cars.clear()
                intersections.clear()

    # 게임 상태별 화면 출력 및 로직 처리
    if game_state == "menu":
        draw_text_center("Traffic Simulator")
        start_button.draw()

    elif game_state == "input":
        draw_text_center("Enter number of intersections (1-10):")
        # 입력 박스 그리기
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

            # 차량 이동 및 충돌 검사
            for car in cars:
                car.move()

            if not crash_enabled:
                for i1 in range(len(cars)):
                    for i2 in range(i1 + 1, len(cars)):
                        c1, c2 = cars[i1], cars[i2]
                        rect1 = pygame.Rect(c1.x, c1.y, c1.width, c1.height)
                        rect2 = pygame.Rect(c2.x, c2.y, c2.width, c2.height)
                        if rect1.colliderect(rect2):
                            car_crashed = True
                            paused = True

            # 화면 밖 차량 제거
            cars = [c for c in cars if not c.is_off_screen()]

        for car in cars:
            car.draw()

        # 충돌 발생 시 메시지 출력
        if car_crashed:
            draw_text_center("Car Crashed!", 50)

        # 충돌 토글 상태 표시
        status_text = "Collision Detection: ON" if not crash_enabled else "Collision Detection: OFF"
        status_surf = font.render(status_text, True, RED if crash_enabled else GREEN)
        screen.blit(status_surf, (10, 10))

        # 일시정지 상태 표시
        if paused:
            draw_text_center("Paused", 100)

    pygame.display.flip()
    clock.tick(60)
