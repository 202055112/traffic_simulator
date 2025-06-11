# 베이스 이미지
FROM python:3.11-slim

# 필수 도구 설치 (x11, pygame 실행용)
RUN apt-get update && apt-get install -y \
    xvfb \
    x11-utils \
    python3-tk \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 코드 복사
COPY . .

# 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 스크립트 실행 (X 가상 화면을 사용)
CMD ["xvfb-run", "python", "Traffic Simulator.py"]

# Dockerfile
FROM python:3.10-slim

# 시스템 패키지 설치 (pygame에 필요한 라이브러리)
RUN apt-get update && apt-get install -y \
    python3-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev \
    libsdl1.2-dev libsmpeg-dev libportmidi-dev libavformat-dev libswscale-dev \
    libjpeg-dev libfreetype6-dev xvfb x11-xserver-utils \
    && apt-get clean

# 작업 디렉토리 설정
WORKDIR /app

# 파일 복사
COPY . .

# 파이썬 의존성 설치
RUN pip install --upgrade pip \
    && pip install pygame
