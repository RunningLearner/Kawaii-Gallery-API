# 베이스 이미지 설정
FROM python:3.9-slim

# 환경 변수 설정: Python 출력 버퍼링 해제
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리 설정
WORKDIR /app

# 애플리케이션 코드 복사
COPY ./app ./app

# 종속성 파일 복사 및 설치
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# FastAPI 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
