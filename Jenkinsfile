pipeline {
    agent any
    
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        FRONTEND_IMAGE = 'ewiabeng23/job-hunter-frontend'
        BACKEND_IMAGE = 'ewiabeng23/job-hunter-backend'
        K8S_NAMESPACE = 'job-hunter'
        SONAR_URL = 'http://af8b0136249d444aab8138790d39ab56-687225748.us-east-1.elb.amazonaws.com'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Pulling code from GitHub...'
                git branch: 'main',
                    credentialsId: 'github-credentials',
                    url: 'https://github.com/ewiabeng23/AI-job-hunter.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    withSonarQubeEnv('sonarqube') {
                        sh '''
                            curl -o /tmp/sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
                            unzip -o /tmp/sonar-scanner.zip -d /tmp/
                            /tmp/sonar-scanner-5.0.1.3006-linux/bin/sonar-scanner \
                                -Dsonar.projectKey=job-hunter \
                                -Dsonar.sources=. \
                                -Dsonar.host.url=${SONAR_URL} \
                                -Dsonar.token=${SONAR_AUTH_TOKEN}
                        '''
                    }
                }
            }
        }
        
        stage('Build Backend') {
            steps {
                echo 'Building backend Docker image...'
                sh 'docker build -t ${BACKEND_IMAGE}:${BUILD_NUMBER} ./backend'
                sh 'docker tag ${BACKEND_IMAGE}:${BUILD_NUMBER} ${BACKEND_IMAGE}:latest'
            }
        }
        
        stage('Build Frontend') {
            steps {
                echo 'Building frontend Docker image...'
                sh 'docker build -t ${FRONTEND_IMAGE}:${BUILD_NUMBER} ./frontend'
                sh 'docker tag ${FRONTEND_IMAGE}:${BUILD_NUMBER} ${FRONTEND_IMAGE}:latest'
            }
        }

        stage('Trivy Security Scan') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh '''
                        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
                        trivy image --exit-code 0 --severity HIGH,CRITICAL ${BACKEND_IMAGE}:${BUILD_NUMBER}
                        trivy image --exit-code 0 --severity HIGH,CRITICAL ${FRONTEND_IMAGE}:${BUILD_NUMBER}
                    '''
                }
            }
        }
        
        stage('Push to DockerHub') {
            steps {
                echo 'Pushing images to Docker Hub...'
                sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                sh 'docker push ${BACKEND_IMAGE}:${BUILD_NUMBER}'
                sh 'docker push ${BACKEND_IMAGE}:latest'
                sh 'docker push ${FRONTEND_IMAGE}:${BUILD_NUMBER}'
                sh 'docker push ${FRONTEND_IMAGE}:latest'
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying to Kubernetes...'
                sh 'kubectl rollout restart deployment/backend -n ${K8S_NAMESPACE}'
                sh 'kubectl rollout restart deployment/frontend -n ${K8S_NAMESPACE}'
                sh 'kubectl rollout status deployment/backend -n ${K8S_NAMESPACE}'
                sh 'kubectl rollout status deployment/frontend -n ${K8S_NAMESPACE}'
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        unstable {
            echo '⚠️ Pipeline completed with warnings - check SonarQube or Trivy results!'
        }
        failure {
            echo '❌ Pipeline failed! Check logs above.'
        }
    }
}
