FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 환경 변수: 로컬 X 서버와 연동 (리눅스 기준)
ENV DISPLAY=:0
ENV SDL_VIDEODRIVER=x11

CMD ["python", "main.py"]
