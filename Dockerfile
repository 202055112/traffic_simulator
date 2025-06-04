FROM python:3.10-slim

# 기본 패키지 설치
RUN apt-get update && apt-get install -y \
    python3-dev python3-pip \
    python3-setuptools \
    python3-opengl \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libsm6 libxext6 libxrender-dev libx11-dev \
    x11-xserver-utils && \
    pip install pygame

# 앱 디렉토리 복사
WORKDIR /app
COPY . /app

CMD ["python", "your_main.py"]
