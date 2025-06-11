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

traffic-simulator/
├── assets/
│   ├── images/               # 차, 신호등 이미지 넣을 폴더 (현재는 안 쓰지만 확장 대비)
│   └── sounds/               # 사운드 효과 (선택 사항)
├── src/
│   ├── __init__.py
│   ├── main.py               # 프로그램 실행 메인 파일
│   ├── simulation.py         # 게임 로직 (도로, 차, 교차로 등)
│   ├── ui.py                 # 버튼 및 UI 관련 코드
│   └── config.py             # 설정 값들 (화면 크기, 색상 등)
├── README.md                 # 프로젝트 설명 문서
├── requirements.txt          # 필요한 라이브러리 목록 (pygame 등)
├── .gitignore                # Git에서 무시할 파일들 (.pyc, __pycache__ 등)
└── LICENSE                   # (선택) MIT 라이선스 등 오픈소스 라이선스


