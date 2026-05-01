# HireFlow

A local-first tool that connects to your Gmail, uses AI to parse job-related emails, and displays your application history on a web dashboard.

## Features

- Gmail OAuth login (just click "Sign in with Google")
- AI-powered email classification using Claude (detects applications, interviews, offers, rejections, etc.)
- Dynamic interview funnels: each company can have different stages
- Incremental sync: only processes new emails on subsequent runs
- Local web dashboard with stats, funnel charts, timeline, and activity graphs
- All data stays local in a SQLite database

## Prerequisites

- Python 3.11+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- An [Anthropic API key](https://console.anthropic.com/)

## Setup

### 1. Clone and install

```bash
git clone <repo-url>
cd hireflow

# Install Python dependencies
uv sync

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure environment

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Set up Google OAuth (one-time, for repo maintainer)

If `credentials.json` is not included in the repo, you need to create it:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Gmail API
4. Go to Credentials > Create Credentials > OAuth 2.0 Client ID
5. Application type: Web application
6. Add `http://localhost:8000/api/auth/callback` as an authorized redirect URI
7. Download the JSON and save it as `credentials.json` in the project root

## Usage

### Start the backend

```bash
uv run uvicorn backend.main:app --reload --port 8000
```

### Start the frontend (in another terminal)

```bash
cd frontend
npm run dev
```

### Open the app

1. Go to `http://localhost:5173`
2. Navigate to Settings
3. Click "Connect Gmail" and authorize access
4. Set a start date and click "Sync Now"
5. Navigate to Dashboard to see your results

## How It Works

1. The app fetches emails matching job-related keywords (application, interview, offer, etc.) from your Gmail
2. Each email is sent to Claude AI for classification
3. Claude extracts: company name, role title, event type (applied, phone screen, onsite, offer, rejection, etc.), and a summary
4. Results are stored in a local SQLite database (`data/tracker.db`)
5. The dashboard aggregates and visualizes your application history

## Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: React, TypeScript, Tailwind CSS, Plotly
- **Database**: SQLite
- **AI**: Claude API (Anthropic)
- **Auth**: Google OAuth 2.0
