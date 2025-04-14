# Resume Master Agent

A complete system for streamlining your job application process with AI-powered resume tailoring. This project includes a Chrome extension that integrates with LinkedIn job listings and a backend server that manages your applications and automatically generates tailored resumes for each position.

## Features

- **LinkedIn Integration**: Browser extension that works directly on LinkedIn job listings
- **Job Tracking**: Save jobs, track application status, and set goals for daily applications
- **AI Resume Tailoring**: Automatically generate custom-tailored resumes for each job based on the job description
- **Application Dashboard**: View all saved jobs and their statuses in one place
- **Resume Parser**: Advanced PDF resume parsing with section detection and structured data extraction

## Project Structure

```
resume_master_agent/
├── backend/               # Flask backend server
│   ├── app.py            # Main application file
│   ├── database.py       # Database models and utilities
│   ├── resume_parser/    # Resume parsing module
│   └── api/              # API endpoints
├── extension/            # Chrome extension
│   ├── manifest.json     # Extension configuration
│   ├── content.js        # LinkedIn page integration
│   ├── background.js     # Background service worker
│   └── popup/           # Extension UI components
├── tools/               # Utility tools
│   ├── llm_api.py       # LLM integration (Claude, GPT-4)
│   ├── web_scraper.py   # Web scraping utilities
│   └── search_engine.py # Search functionality
├── tests/               # Test suite
│   ├── resume_parser/   # Parser tests
│   └── fixtures/        # Test data
├── docs/                # Documentation
└── data/                # Data storage
```

## Installation and Setup

### Prerequisites

- Python 3.8+
- Chrome web browser
- API keys for:
  - Anthropic Claude
  - OpenAI (optional)
  - Azure OpenAI (optional)

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/noTe-Z/resume_master_agent.git
cd resume_master_agent
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the example environment file and update with your settings:
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys and configuration
```

5. Initialize the database:
```bash
cd backend
python -c "from app import init_db; init_db(); print('Database initialized successfully!')"
```

6. Run the backend server:
```bash
cd backend
flask run --host=0.0.0.0 --port=3000
```

The server will start on http://localhost:3000

### Browser Extension Installation

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in the top right)
3. Click "Load unpacked" and select the `extension` folder
4. The extension should now appear in your browser toolbar

## Development

### Setting Up Development Environment

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

### Code Style

We follow PEP 8 guidelines and use type hints. Key points:
- Use 4 spaces for indentation
- Maximum line length of 88 characters (Black formatter)
- Document functions and classes with docstrings
- Add type hints to function parameters and return values

### Running Tests

Run the full test suite:
```bash
python -m pytest
```

Run specific test categories:
```bash
python -m pytest tests/resume_parser  # Only parser tests
python -m pytest tests/test_api.py    # Only API tests
```

### Database Migrations

We use Flask-Migrate for database migrations:

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Anthropic Claude](https://www.anthropic.com/claude) for AI capabilities
- [LinkedIn](https://www.linkedin.com) for job data integration
- All contributors who have helped shape this project
