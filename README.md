# 🛣️ 스마트 교통 시뮬레이터

Python과 Pygame으로 구현한 동적이고 인터랙티브한 교통 시뮬레이션 게임입니다.  
사용자가 교차로 개수를 입력하면 랜덤으로 배치되고, 신호등과 차량이 교통 흐름을 현실감 있게 재현합니다.

---

## 📌 주요 기능

- 🚦 **신호등 시스템**: 교차로마다 신호등이 작동하며, 차량은 신호에 맞춰 정지하거나 통과합니다.  
- 🚗 **차량 인공지능**: 차량은 좌/우/직진 방향으로 움직이며, 앞차와 충돌하지 않도록 거리 유지 기능 포함.  
- 🔁 **충돌 시뮬레이션 토글**: `P` 키로 차량 충돌 시뮬레이션 기능을 켜고 끌 수 있습니다. 충돌 시 “Car Crashed!” 메시지가 표시됩니다.  
- 🛑 **일시 정지/재개**: 스페이스바로 시뮬레이션을 일시 정지하거나 재개할 수 있습니다.  
- 📍 **랜덤 교차로 생성**: 사용자가 입력한 수만큼 교차로를 무작위로 생성합니다.  
- 🖱️ **간단한 UI 버튼**: 시작, 충돌 방지 토글 버튼 등이 포함되어 있습니다.  


---

## 🚀 실행 방법


### 1. Docker Compose 이용
### 2. Traffic Simulator.py 실행

```bash
docker-compose up
# -

## 수동 실행시
git clone https://github.com/202055112/traffic_simulator.git
cd traffic-simulator
xhost +local:docker
docker-compose up --build

---

### 2. Traffic Simulator.py 실행

1. pip install pygame
2. pygame 설치 후 실행

---

| 키       | 동작             |
| ------- | -------------- |
| `P`     | 차량 충돌 시뮬레이션 토글 |
| `SPACE` | 시뮬레이션 일시정지/재개  |
| `ESC`   | 메인 메뉴로 돌아가기    |
| 마우스 클릭  | 버튼 클릭          |

traffic-simulator/             # 프로젝트 루트 폴더
│
├── .github/                   # 깃허브 워크플로우 설정
│   └── workflows/
│       └── ci.yml             # 예: CI/CD 워크플로우 파일
│
├── src/                       # 소스 코드 폴더
│   └── traffic_simulator.py   # 메인 시뮬레이터 파이썬 파일
│
├── docker/                    # 도커 관련 파일 모음 (선택사항)
│   ├── Dockerfile             # 도커 이미지 빌드 스크립트
│   └── docker-compose.yml     # 도커 컴포즈 설정
│
├── tests/                     # 테스트 코드 폴더
│   └── test_traffic.py        # 테스트 예시
│
├── requirements.txt           # 파이썬 패키지 의존성 목록
├── README.md                  # 프로젝트 설명 문서
├── LICENSE                    # 라이선스 (MIT)




| 기능                   | 설명                           |
| -------------------- | ---------------------------- |
| `measure_time` 데코레이터 | 함수 실행 시간 측정                  |
| `lambda`             | 오프스크린 차량 필터링에 사용             |
| `try-except`         | 메인 루프 전체 예외 처리               |
| 문서화                  | 각 클래스 및 함수에 docstring과 주석 추가 |
| 교차로/신호등              | 전체 맵에 격자형 자동 배치 및 주기적 전환     |
| 충돌 감지                | 차량 간 충돌 감지 및 멈춤              |
