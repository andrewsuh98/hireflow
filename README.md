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

- Python 3.12+
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

### 3. Set up Google OAuth

The `credentials.json` file identifies your app, not any specific user. Each person who uses the app authenticates with their own Google account through the OAuth consent screen.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown (top-left) > **New Project**. Name it "HireFlow" and create it.
3. Select your new project in the dropdown.

**Enable the Gmail API:**

4. Go to **APIs & Services** > **Library** in the left sidebar.
5. Search for "Gmail API", click it, then click **Enable**.

**Configure the OAuth consent screen:**

6. Go to **APIs & Services** > **OAuth consent screen**.
7. Click **Get Started** (or **Configure Consent Screen**).
8. Choose **Internal** if you have a Google Workspace account, otherwise choose **External**.
9. Fill in App name ("HireFlow"), support email, and developer contact email. Click **Save and Continue**.
10. On the Scopes screen, click **Add or Remove Scopes**, find `https://www.googleapis.com/auth/gmail.readonly`, check it, then click **Update** and **Save and Continue**.
11. If you chose External: on the Test users screen, click **Add Users** and add your Gmail address. Only test users can log in while the app is in Testing mode.

**Create the OAuth credential:**

12. Go to **APIs & Services** > **Credentials**.
13. Click **+ Create Credentials** > **OAuth client ID**.
14. Application type: **Web application**. Name it anything (e.g., "HireFlow Web Client").
15. Under **Authorized redirect URIs**, click **Add URI** and enter: `http://localhost:8000/api/auth/callback`
16. Click **Create**.
17. Download the JSON from the dialog that appears and save it as `credentials.json` in the project root.

## Usage

### Start the backend

```bash
uv run python -m uvicorn backend.main:app --reload --port 8000
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
