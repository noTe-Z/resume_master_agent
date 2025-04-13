# Resume Master Agent

A complete system for streamlining your job application process with AI-powered resume tailoring. This project includes a Chrome extension that integrates with LinkedIn job listings and a backend server that manages your applications and automatically generates tailored resumes for each position.

## Features

- **LinkedIn Integration**: Browser extension that works directly on LinkedIn job listings
- **Job Tracking**: Save jobs, track application status, and set goals for daily applications
- **AI Resume Tailoring**: Automatically generate custom-tailored resumes for each job based on the job description
- **Application Dashboard**: View all saved jobs and their statuses in one place

## Project Structure

The project consists of three main components:

1. **Backend Server**: Flask-based API for job storage and resume tailoring
2. **Browser Extension**: Chrome extension for LinkedIn integration
3. **Utility Tools**: Web scraping, search, and AI modules

## Installation and Setup

### Prerequisites

- Python 3.8+
- Chrome web browser
- Anthropic API key (for Claude AI access)

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

4. Create a `.env` file in the `backend` directory with your API keys:
```
ANTHROPIC_API_KEY=your_api_key_here
```

5. Run the backend server:
```bash
cd backend
flask run
```

The server will start on http://localhost:5000

### Browser Extension Installation

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in the top right)
3. Click "Load unpacked" and select the `extension` folder from this repository
4. The LinkedIn Job Saver extension should now be installed and visible in your extensions toolbar

## Usage

### Saving Jobs from LinkedIn

1. Browse job listings on LinkedIn
2. When viewing a job you're interested in, click the extension icon in your browser toolbar
3. Click "Save Job" to add it to your database

### Managing Your Job Applications

1. Click the extension icon and select "View Saved Jobs"
2. You'll see a dashboard with all your saved jobs
3. Update status to "Applied" or "Interviewing" as you progress
4. Track your daily application goals

### Generating Tailored Resumes

1. From your jobs dashboard, select a saved job
2. Click "Tailor Resume"
3. The AI will generate a customized resume based on the job description
4. Review and download the tailored resume

## Development

### Project Components

- `backend/app.py`: Main Flask application with API endpoints
- `backend/database.py`: Database connection and utilities
- `extension/`: Chrome extension files
  - `manifest.json`: Extension configuration
  - `content.js`: LinkedIn page integration
  - `background.js`: Background service worker
  - `popup/`: UI components for the extension
- `tools/`: Utility functions
  - `llm_api.py`: Integration with Anthropic Claude API
  - `web_scraper.py`: Web scraping utilities
  - `search_engine.py`: Search functionality

### Running Tests

The project includes comprehensive test coverage:

```bash
cd tests
pytest
```

## License

MIT License - See LICENSE file for details.
