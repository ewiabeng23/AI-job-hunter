# 🚀 Job Hunter AI - SaaS Platform

AI-powered job application assistant that helps users find jobs, generates custom CVs, and writes personalized cover letters.

## Features

- 🔐 User Authentication (JWT)
- 📄 CV Management (Multiple CVs per user)
- 🔍 AI Job Search (LinkedIn, Indeed, Glassdoor)
- 🎯 Smart Filtering (Salary, Location, Keywords, Remote)
- 🤖 AI-Powered CV Customization (Claude Sonnet 4.5)
- ✉️ AI Cover Letter Generation
- 📊 Application Tracking
- 💰 Usage Limits (Free: 5/month, upgradable)

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **AI:** Anthropic Claude Sonnet 4.5
- **Auth:** JWT + bcrypt
- **Deployment:** Docker + Kubernetes

## Quick Start

### Local Development
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py

# Runs on http://localhost:8001
```

### Docker
```bash
docker-compose up
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

## API Endpoints

- `POST /auth/signup` - Create account
- `POST /auth/login` - Login
- `GET /auth/me` - Get current user
- `POST /cvs` - Create CV
- `GET /cvs` - List CVs
- `POST /jobs/search` - Search jobs
- `POST /jobs/apply` - Apply with AI
- `GET /applications` - List applications

## Environment Variables
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/jobhunter
ANTHROPIC_API_KEY=your_api_key
SECRET_KEY=your_secret_key
```

## License

MIT

## Author

Built with ❤️ using Claude AI
