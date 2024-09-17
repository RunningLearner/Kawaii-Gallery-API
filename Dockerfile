# 베이스 이미지 설정
FROM python:3.11-slim

# 필요한 패키지 업데이트 및 설치 (OpenGL 관련 라이브러리 포함)
RUN apt-get update && apt-get install -y \
    build-essential \
    libopencv-dev \
    python3-opencv \
    libgl1-mesa-glx \  # OpenGL 관련 라이브러리 설치
    && rm -rf /var/lib/apt/lists/*
    
# 작업 디렉토리 설정
WORKDIR /app

# 종속성 파일 복사 및 설치
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
