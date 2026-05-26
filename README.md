# Job Hunter AI - Production-Grade SaaS Platform

An AI-powered job application assistant built with a full DevOps pipeline, deployed on AWS EKS with GitLab CI/CD, Terraform infrastructure as code, and automated E2E testing.

Live at: https://jobhunter.wigsbydiko.co.uk

## Features

- User Authentication - JWT-based auth with bcrypt password hashing
- CV Management - Upload and manage multiple CVs
- Real Job Search - Live jobs via Adzuna API (UK, US, AU, CA)
- Easy Apply Filter - Filter jobs that support one-click applications
- AI CV Tailoring - Claude AI customises your CV for each job
- CV Humaniser - Rewrites AI content to bypass AI detection tools
- Cover Letter Generation - Personalised cover letters per application
- Match Scoring - AI scores how well you match each job
- Interview Prep - AI generates likely interview questions per role
- Application Tracking - Track all your applications in one place
- Subscription Tiers - Free (5/month) and Pro plans

## Tech Stack

- Frontend: React, Vite, Axios
- Backend: Python FastAPI, SQLAlchemy
- Database: PostgreSQL
- AI: Anthropic Claude Sonnet
- Job Data: Adzuna Jobs API
- Container: Docker
- Orchestration: Kubernetes (AWS EKS)
- Package Manager: Helm
- Ingress: Traefik
- SSL: Let's Encrypt (ACME)
- CI/CD: GitLab CI
- IaC: Terraform
- Monitoring: Prometheus + Grafana + Alertmanager
- Security Scanning: Trivy
- Testing: Playwright E2E

## Infrastructure

All infrastructure is provisioned via Terraform on AWS:

- VPC with public/private subnets across 2 AZs
- EKS 1.34 with managed node group (t3.medium x 2)
- AWS Load Balancer Controller via IRSA
- Internet-facing NLB via Traefik
- S3 remote state backend with versioning
- Prometheus + Grafana monitoring stack

To provision:
  cd terraform
  terraform init
  terraform plan
  terraform apply

## CI/CD Pipeline

GitLab CI pipeline with 6 stages:

1. scan-source - Trivy scans source code for vulnerabilities
2. build - Docker builds backend and frontend images, pushes to DockerHub
3. scan-images - Trivy scans built Docker images
4. deploy - Helm deploys to EKS, triggers rolling restart
5. health-check - Verifies pods and services are running
6. e2e-tests - Playwright tests run against live environment

Required GitLab CI/CD Variables:
- DOCKERHUB_TOKEN - DockerHub access token
- DOCKERHUB_USER - DockerHub username
- AWS_ACCESS_KEY_ID - AWS access key
- AWS_SECRET_ACCESS_KEY - AWS secret key
- KUBECONFIG_DATA - Base64 encoded kubeconfig

## Getting Started

Prerequisites:
- AWS CLI configured
- kubectl installed
- Helm 3.x installed
- Docker installed

Local Development:

1. Clone the repo:
   git clone https://github.com/ewiabeng23/AI-job-hunter.git
   cd AI-job-hunter

2. Set up environment variables:
   cp .env.example .env
   Edit .env with your actual values

3. Run with Docker Compose:
   docker-compose up

4. Access the app:
   Frontend: http://localhost:80
   Backend API: http://localhost:8001

Production Deployment:

1. Provision infrastructure:
   cd terraform
   terraform init
   terraform apply

2. Configure kubectl:
   aws eks update-kubeconfig --region us-east-1 --name job-hunter-cluster

3. Create Kubernetes secrets:
   kubectl create secret generic job-hunter-secrets \
     --namespace job-hunter \
     --from-literal=database-url="YOUR_DATABASE_URL" \
     --from-literal=secret-key="YOUR_JWT_SECRET" \
     --from-literal=anthropic-api-key="YOUR_ANTHROPIC_KEY" \
     --from-literal=adzuna-app-id="YOUR_ADZUNA_ID" \
     --from-literal=adzuna-app-key="YOUR_ADZUNA_KEY"

4. Deploy via Helm:
   helm upgrade --install job-hunter ./helm/job-hunter \
     --namespace job-hunter \
     --create-namespace \
     --values ./helm/job-hunter/values.yaml

## API Documentation

- POST /api/auth/signup - Register new user
- POST /api/auth/login - Login
- GET  /api/auth/me - Get current user
- POST /api/cvs - Create CV
- GET  /api/cvs - List CVs
- DELETE /api/cvs/{id} - Delete CV
- POST /api/jobs/search - Search jobs
- POST /api/jobs/apply - AI-tailored apply
- GET  /api/applications - List applications
- DELETE /api/applications/{id} - Delete application

## Testing

Playwright E2E tests covering:
- Authentication (login, logout, signup navigation)
- Job search and filtering
- Dashboard navigation
- CV management

Run locally:
  cd tests
  npm install
  npx playwright install chromium
  npx playwright test
  npx playwright show-report

Tests run automatically in the GitLab CI pipeline on every push to main.

## Monitoring

- Prometheus - Metrics collection
- Grafana - Dashboards and visualisation
- Alertmanager - Alert routing and notification

## Security

- No hardcoded credentials - all secrets via Kubernetes Secrets
- Trivy scanning - source code and Docker images on every pipeline run
- JWT authentication - stateless token-based auth
- bcrypt - password hashing
- HTTPS only - SSL via Let's Encrypt
- Private subnets - EKS nodes in private subnets, only ELB is public
- IAM least privilege - IRSA for Load Balancer Controller

## Author

Lovert - DevOps Engineer
GitHub: https://github.com/ewiabeng23

## License

MIT License

Built with Claude AI, AWS, Kubernetes, and GitLab CI
# Last updated: Tue May 26 22:08:08 UTC 2026
# triggered: Tue May 26 22:22:41 UTC 2026
