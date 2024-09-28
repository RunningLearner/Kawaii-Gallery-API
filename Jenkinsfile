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
        stage('Prepare Firebase Key') {
            steps {
                script {
                    // Firebase 크리덴셜 파일을 임시 경로에서 복사
                    withCredentials([file(credentialsId: 'firebase_keyfile_kawaii_gallery', variable: 'FIREBASE_KEY_PATH')]) {
                        // Firebase 키 파일을 복사하여 workspace에 저장
                        sh 'cp $FIREBASE_KEY_PATH firebase-adminsdk.json'
                    }
                }
            }
        }
        stage('Build and Deploy') {
            steps {
                script {
                    // .env 파일 생성 (Jenkins 환경 변수에서 값 설정)
                    writeFile file: '.env', text: "API_ENV=${API_ENV}\n"
                    
                    // Firebase 크리덴셜 파일 생성 (컨테이너에 복사할 준비)
                    writeFile file: 'firebase-adminsdk.json', text: "${FIREBASE_KEY_CRED}"

                    // 호스트의 현재 작업 디렉토리 확인
                    sh 'pwd'

                    // 기존 컨테이너 중지 및 제거 (볼륨 포함) 
                    // TODO: 프로덕션 단계에서는 볼륨 제거 옵션 삭제하기
                    sh 'docker-compose -f ${COMPOSE_FILE} down --volumes'
                    
                    // Docker 빌드 시 캐시를 사용하지 않고 빌드
                    sh 'docker-compose -f ${COMPOSE_FILE} build --no-cache'

                    // 강제로 컨테이너를 재생성하여 최신 코드 반영
                    sh 'docker-compose -f ${COMPOSE_FILE} up --force-recreate -d'
                }
            }
        }
    }
}
