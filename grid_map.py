import pygame

# pygame 서브모듈 초기화
pygame.init()

WIDTH, HEIGHT=800,600 #가로세로 픽셀
GRID_SIZE=40 # 한칸의 그리드 셀 크기를 40x40 픽셀
ROWS=HEIGHT//GRID_SIZE
COLS=WIDTH//GRID_SIZE # 행과 열 계산: 15x20의 격자 생성
WHITE=(255, 255, 255)
GRAY=(200, 200, 200)
BLACK=(0, 0, 0)
ROAD_COLOR=(100, 100, 100) #RGB 값 정의

# 디스플레이 세팅
screen=pygame.display.set_mode((WIDTH, HEIGHT)) #설정한 크기의 창 생성, screen이라는 변수에 저장
pygame.display.set_caption("Smart Traffic Simulator") #창 제목

# Clock
clock = pygame.time.Clock() #초당 프레임

# 길의 정의 (1 = road, 0 = empty)
# 하나의 교차로 예시
road_map=[[0 for _ in range(COLS)] for _ in range(ROWS)] #2차원 배열
for i in range(ROWS):
    road_map[i][5]=1  #6번째 열에 수직 도로
for j in range(COLS):
    road_map[7][j]=1  #8번째 행에 수평 도로

# 그리드라인과 길 생성
def draw_grid():
    for i in range(ROWS):
        for j in range(COLS):
            rect = pygame.Rect(j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE) # 각 격자의 사각형 생성, j=0,i=0일때 0,0에 40x40 사각형 생성
            if road_map[i][j] == 1:
                pygame.draw.rect(screen, ROAD_COLOR, rect) #셀이 1이면 도로(색칠)
            else:
                pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, GRAY, rect, 1) #모든 셀 위에 회색 테두리를 얇게 그림

# 게임 실행 메인 루프
running = True
while running: #게임 상태 지속
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False #모든 이벤트를 확인하고 닫기 버튼 클릭시 종료

    draw_grid()
    pygame.display.flip() #실제 화면으로 보여줌
    clock.tick(60) #초당 60초 프레임

pygame.quit()
