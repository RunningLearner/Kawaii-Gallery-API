# Kawaii-Gallery-API

오늘의 귀여움 api

# How to start app

1. `python3 -m venv myenv` 가상환경을 만듭니다.

1. [win]`myenv\Scripts\activate`, [mac]`source myenv/bin/activate` 가상환경을 실행합니다.

1. `pip install -r requirements.txt` 필요한 패키지들을 설치합니다.

1. `pip freeze > requirements.txt` 새로 설치된 패키지를 추가합니다.

1. `uvicorn app.main:app --reload` 루트디렉터리에서 앱을 시작합니다.

---

# How to start with DB

1. `docker-compose up -d` 루트 디렉터리에서 도커컴포즈를 실행합니다.

### 종료

`deactivate` 가상환경을 종료합니다.
