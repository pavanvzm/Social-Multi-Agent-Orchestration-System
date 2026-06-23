# Multi-Agent Market Research Orchestration System

An AI-powered market research platform that orchestrates multiple specialized agents to generate comprehensive research reports collaboratively.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)

## 🎯 Overview

This system democratizes enterprise-grade market research by orchestrating multiple AI agents that work collaboratively, mimicking how human research teams operate but at scale and speed.

### Key Features

- **Multi-Agent Architecture**: Research, Writer, Planning, and Reviewer agents working in concert
- **Real-Time Orchestration**: Dynamic task decomposition and agent coordination
- **Source Credibility Scoring**: Automatic assessment of research sources
- **PDF Export**: Professional report generation with citations
- **Modern Web Interface**: React-based dashboard with live agent activity tracking

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Environment Variables

Create a `.env` file in the backend directory if needed:

```env
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=*
```

## 📁 Project Structure

```
├── backend/
│   ├── agents/           # AI agent implementations
│   │   ├── research_agent.py   # Research data collection
│   │   └── writer_agent.py     # Content generation
│   ├── api/              # FastAPI endpoints
│   │   └── main.py       # REST API routes
│   ├── core/             # Core orchestration engine
│   │   ├── orchestrator.py     # Workflow engine
│   │   └── types.py      # Data models
│   ├── services/         # Business services
│   │   └── pdf_service.py      # PDF generation
│   └── requirements.txt  # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page views
│   │   ├── hooks/        # Custom React hooks
│   │   ├── utils/        # API client
│   │   └── types/        # TypeScript definitions
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

## 🏗️ Architecture

### Agent Types

| Agent | Purpose |
|-------|---------|
| **Research Agent** | Collects sources, scrapes authorized data, scores credibility |
| **Writer Agent** | Generates report content with proper citations and tone |
| **Planning Agent** | (Planned) Creates report outlines and structure |
| **Reviewer Agent** | (Planned) Validates facts and consistency |

### Workflow

```
User Input → Orchestrator → Task Decomposition
                                  ↓
                    ┌─────────────┴─────────────┐
                    ↓                           ↓
              Research Phase              Writing Phase
                    ↓                           ↓
              Source Collection            Content Generation
                    ↓                           ↓
                    └─────────────┬─────────────┘
                                  ↓
                           Review & Export
                                  ↓
                            PDF Report
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/projects` | Create new project |
| `GET` | `/api/projects` | List all projects |
| `GET` | `/api/projects/{id}` | Get project details |
| `DELETE` | `/api/projects/{id}` | Delete project |
| `POST` | `/api/projects/{id}/execute` | Run full workflow |
| `GET` | `/api/projects/{id}/events` | Get workflow events |
| `GET` | `/api/projects/{id}/sources` | Get research sources |
| `PATCH` | `/api/projects/{id}/sections/{sid}` | Update section |
| `GET` | `/api/projects/{id}/export/pdf` | Export as PDF |

## 🎨 UI Preview

### Dashboard
- Project grid with status badges
- Quick-create modal for new research
- Real-time project list

### Workspace
- **Left Panel**: Agent activity with progress indicators
- **Center Panel**: Live content preview with section editing
- **Right Panel**: Research sources with credibility scores

## 🔧 Development

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Code Style

- Backend: Black formatter, flake8 linting
- Frontend: ESLint, Prettier

## 📊 Roadmap

### Phase 1 - MVP ✅
- [x] Core orchestration engine
- [x] Research + Writer agents (simulated)
- [x] Web application
- [x] PDF export
- [x] Single-user mode

### Phase 2 - Enhancement (Planned)
- [ ] Planning Agent implementation
- [ ] Reviewer Agent implementation
- [ ] iOS application
- [ ] Team collaboration
- [ ] Template library

### Phase 3 - Scale (Planned)
- [ ] Android application
- [ ] API for integrations
- [ ] Mobile widgets
- [ ] Voice input

### Phase 4 - Enterprise (Planned)
- [ ] SSO integration
- [ ] Custom agent training
- [ ] White-label options
- [ ] Advanced security

## 🔒 Security

- OAuth 2.0 + JWT authentication (planned)
- End-to-end encryption (planned)
- Role-based access control (planned)
- Regular security audits (planned)

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

*This system was built following the PRD specifications for a Multi-Agent Market Research Orchestration Platform.*
