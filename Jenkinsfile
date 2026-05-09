pipeline {
    agent any

    environment {
        DOCKERHUB_USER   = 'ewiabeng23'
        BACKEND_IMAGE    = "${DOCKERHUB_USER}/job-hunter-backend"
        FRONTEND_IMAGE   = "${DOCKERHUB_USER}/job-hunter-frontend"
        IMAGE_TAG        = "${BUILD_NUMBER}"
        K8S_NAMESPACE    = 'job-hunter'
        JENKINS_NS       = 'jenkins'
        KUBECONFIG_PATH  = "/tmp/kubeconfig-${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Pulling code from GitHub..."
                git branch: 'main',
                    credentialsId: 'GitHub-Cred',
                    url: 'https://github.com/ewiabeng23/AI-job-hunter.git'
            }
        }

        stage('Trivy - Scan Source Code') {
            steps {
                echo "Scanning source code for vulnerabilities..."
                sh 'trivy fs --exit-code 0 --severity HIGH,CRITICAL --no-progress --format table . || true'
            }
        }

        stage('Build Backend Image - Kaniko') {
            steps {
                echo "Building backend image with Kaniko..."
                withCredentials([string(credentialsId: 'kubeconfig', variable: 'KUBE_CONFIG_DATA')]) {
                    sh '''
                        echo "$KUBE_CONFIG_DATA" | base64 -d > ${KUBECONFIG_PATH}
                        export KUBECONFIG=${KUBECONFIG_PATH}
                        kubectl delete pod kaniko-backend -n ${JENKINS_NS} --ignore-not-found
                        kubectl apply -f kaniko/backend-pod.yaml
                        echo "Waiting for Kaniko backend to complete..."
                        kubectl wait pod/kaniko-backend --for=jsonpath='{.status.phase}'=Succeeded --timeout=300s -n ${JENKINS_NS}
                        kubectl logs kaniko-backend -n ${JENKINS_NS}
                    '''
                }
            }
        }

        stage('Build Frontend Image - Kaniko') {
            steps {
                echo "Building frontend image with Kaniko..."
                withCredentials([string(credentialsId: 'kubeconfig', variable: 'KUBE_CONFIG_DATA')]) {
                    sh '''
                        echo "$KUBE_CONFIG_DATA" | base64 -d > ${KUBECONFIG_PATH}
                        export KUBECONFIG=${KUBECONFIG_PATH}
                        kubectl delete pod kaniko-frontend -n ${JENKINS_NS} --ignore-not-found
                        kubectl apply -f kaniko/frontend-pod.yaml
                        echo "Waiting for Kaniko frontend to complete..."
                        kubectl wait pod/kaniko-frontend --for=jsonpath='{.status.phase}'=Succeeded --timeout=300s -n ${JENKINS_NS}
                        kubectl logs kaniko-frontend -n ${JENKINS_NS}
                    '''
                }
            }
        }

        stage('Trivy - Scan Docker Images') {
            steps {
                echo "Scanning built images for vulnerabilities..."
                sh '''
                    trivy image --exit-code 0 --severity HIGH,CRITICAL --no-progress ${BACKEND_IMAGE}:latest || true
                    trivy image --exit-code 0 --severity HIGH,CRITICAL --no-progress ${FRONTEND_IMAGE}:latest || true
                '''
            }
        }

        stage('Deploy to EKS') {
            steps {
                echo "Deploying to EKS..."
                withCredentials([string(credentialsId: 'kubeconfig', variable: 'KUBE_CONFIG_DATA')]) {
                    sh '''
                        echo "$KUBE_CONFIG_DATA" | base64 -d > ${KUBECONFIG_PATH}
                        export KUBECONFIG=${KUBECONFIG_PATH}
                        kubectl set image deployment/backend job-hunter-backend=${BACKEND_IMAGE}:latest -n ${K8S_NAMESPACE}
                        kubectl set image deployment/frontend job-hunter-frontend=${FRONTEND_IMAGE}:latest -n ${K8S_NAMESPACE}
                        kubectl rollout status deployment/backend -n ${K8S_NAMESPACE} --timeout=5m
                        kubectl rollout status deployment/frontend -n ${K8S_NAMESPACE} --timeout=5m
                    '''
                }
            }
        }

        stage('Health Check') {
            steps {
                withCredentials([string(credentialsId: 'kubeconfig', variable: 'KUBE_CONFIG_DATA')]) {
                    sh '''
                        echo "$KUBE_CONFIG_DATA" | base64 -d > ${KUBECONFIG_PATH}
                        export KUBECONFIG=${KUBECONFIG_PATH}
                        echo "=== Pods ==="
                        kubectl get pods -n ${K8S_NAMESPACE}
                        echo "=== Services ==="
                        kubectl get svc -n ${K8S_NAMESPACE}
                        echo "=== Ingress ==="
                        kubectl get ingress -n ${K8S_NAMESPACE}
                    '''
                }
            }
        }
    }

    post {
        always {
            sh "rm -f ${KUBECONFIG_PATH}"
        }
        success {
            echo "✅ Build #${IMAGE_TAG} deployed successfully!"
        }
        failure {
            echo "❌ Pipeline failed at build #${IMAGE_TAG} — check logs above."
        }
    }
}
