pipeline {
    agent any
    
    environment {
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

        stage('Build & Push Backend with Kaniko') {
            steps {
                echo 'Building backend image with Kaniko...'
                sh '''
                    kubectl run kaniko-backend \
                        --image=gcr.io/kaniko-project/executor:latest \
                        --restart=Never \
                        --namespace=${K8S_NAMESPACE} \
                        --overrides='{
                            "spec": {
                                "containers": [{
                                    "name": "kaniko-backend",
                                    "image": "gcr.io/kaniko-project/executor:latest",
                                    "args": [
                                        "--context=git://github.com/ewiabeng23/AI-job-hunter.git#refs/heads/main",
                                        "--context-sub-path=backend",
                                        "--dockerfile=backend/Dockerfile",
                                        "--destination=ewiabeng23/job-hunter-backend:latest",
                                        "--destination=ewiabeng23/job-hunter-backend:'"${BUILD_NUMBER}"'"
                                    ],
                                    "volumeMounts": [{
                                        "name": "docker-config",
                                        "mountPath": "/kaniko/.docker"
                                    }]
                                }],
                                "volumes": [{
                                    "name": "docker-config",
                                    "secret": {
                                        "secretName": "dockerhub-secret"
                                    }
                                }],
                                "restartPolicy": "Never"
                            }
                        }' \
                        --wait=true \
                        --timeout=300s
                    kubectl delete pod kaniko-backend -n ${K8S_NAMESPACE}
                '''
            }
        }

        stage('Build & Push Frontend with Kaniko') {
            steps {
                echo 'Building frontend image with Kaniko...'
                sh '''
                    kubectl run kaniko-frontend \
                        --image=gcr.io/kaniko-project/executor:latest \
                        --restart=Never \
                        --namespace=${K8S_NAMESPACE} \
                        --overrides='{
                            "spec": {
                                "containers": [{
                                    "name": "kaniko-frontend",
                                    "image": "gcr.io/kaniko-project/executor:latest",
                                    "args": [
                                        "--context=git://github.com/ewiabeng23/AI-job-hunter.git#refs/heads/main",
                                        "--context-sub-path=frontend",
                                        "--dockerfile=frontend/Dockerfile",
                                        "--destination=ewiabeng23/job-hunter-frontend:latest",
                                        "--destination=ewiabeng23/job-hunter-frontend:'"${BUILD_NUMBER}"'"
                                    ],
                                    "volumeMounts": [{
                                        "name": "docker-config",
                                        "mountPath": "/kaniko/.docker"
                                    }]
                                }],
                                "volumes": [{
                                    "name": "docker-config",
                                    "secret": {
                                        "secretName": "dockerhub-secret"
                                    }
                                }],
                                "restartPolicy": "Never"
                            }
                        }' \
                        --wait=true \
                        --timeout=300s
                    kubectl delete pod kaniko-frontend -n ${K8S_NAMESPACE}
                '''
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
            echo '⚠️ Pipeline completed with warnings!'
        }
        failure {
            echo '❌ Pipeline failed! Check logs above.'
        }
    }
}
