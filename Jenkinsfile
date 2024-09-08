pipeline {
    agent any
    environment {
        COMPOSE_FILE = 'docker-compose.yml' // Docker Compose 파일 이름
        API_ENV = 'prod' // 환경 변수 설정
    }
    stages {
        stage('Checkout') {
            steps {
                // GitHub에서 최신 코드 체크아웃
                git branch: 'main', credentialsId: 'github_access_token', url: 'https://github.com/RunningLearner/Kawaii-Gallery-API.git'
            }
        }
        stage('Build and Deploy') {
            steps {
                script {
                    // .env 파일 생성 (Jenkins 환경 변수에서 값 설정)
                    writeFile file: '.env', text: "API_ENV=${API_ENV}\n"

                    // 기존 컨테이너 중지 및 제거 (볼륨 포함) 
                    // TODO: 프로덕션 단계에서는 볼륨 제거 옵션 삭제하기
                    sh 'docker-compose down --volumes'
                    
                    // Docker 빌드 시 캐시를 사용하지 않고 빌드
                    sh 'docker-compose build --no-cache'

                    // 강제로 컨테이너를 재생성하여 최신 코드 반영
                    sh 'docker-compose up --force-recreate -d'
                }
            }
        }
    }
}
