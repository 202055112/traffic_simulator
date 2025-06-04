FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DISPLAY=:0
ENV SDL_VIDEODRIVER=x11

CMD ["python", "main.py"]

