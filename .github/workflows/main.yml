name: Docker Build and Test

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build_and_test:
    runs-on: ubuntu-latest

    steps:
    - name: 체크아웃 코드
      uses: actions/checkout@v3

    - name: Docker 이미지 빌드
      run: docker build -t traffic-simulator .

    - name: 컨테이너 내에서 테스트 실행 (CLI용)
      run: |
        docker run --rm traffic-simulator python main.py --test-mode

