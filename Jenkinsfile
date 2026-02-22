pipeline {
    agent any
    
    environment {
        FRONTEND_IMAGE = 'ewiabeng23/job-hunter-frontend'
        BACKEND_IMAGE = 'ewiabeng23/job-hunter-backend'
        K8S_NAMESPACE = 'job-hunter'
        PATH = "/var/jenkins_home/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
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

        stage('Build & Push Backend with Kaniko') {
            steps {
                echo 'Building backend image with Kaniko...'
                sh '''
                    kubectl delete pod kaniko-backend -n job-hunter --ignore-not-found
                    kubectl run kaniko-backend \
                        --image=gcr.io/kaniko-project/executor:latest \
                        --restart=Never \
                        --namespace=job-hunter \
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
                    kubectl delete pod kaniko-backend -n job-hunter --ignore-not-found
                '''
            }
        }

        stage('Build & Push Frontend with Kaniko') {
            steps {
                echo 'Building frontend image with Kaniko...'
                sh '''
                    kubectl delete pod kaniko-frontend -n job-hunter --ignore-not-found
                    kubectl run kaniko-frontend \
                        --image=gcr.io/kaniko-project/executor:latest \
                        --restart=Never \
                        --namespace=job-hunter \
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
                    kubectl delete pod kaniko-frontend -n job-hunter --ignore-not-found
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
        failure {
            echo '❌ Pipeline failed! Check logs above.'
        }
    }
}
