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
                    
                    // 기존 컨테이너 중지 및 제거 (존재하는 경우)
                    sh 'docker-compose down'
                    
                    // Docker Compose를 사용해 애플리케이션 빌드 및 배포
                    sh 'docker-compose -f $COMPOSE_FILE up --build -d'
                }
            }
        }
    }
}
