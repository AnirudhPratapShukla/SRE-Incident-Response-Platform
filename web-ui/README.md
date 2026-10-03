# SRE Incident Command Center UI

A professional React/Vite command-center UI for the existing **SRE-Incident-Response-Platform** backend.

## What this replaces

This is a frontend alternative to the current Streamlit presentation layer. The existing FastAPI + LangGraph + Jira + RAG + MCP workflow remains the system of record.

## UI features

- Dark, colorful SRE command-center design
- Incident overview with live workflow pipeline
- AI investigation and evidence view
- Human approval + controlled remediation screen
- Safe Demo Simulation mode
- CloudWatch scan page
- Incident queue with local browser persistence
- API health indicator
- Live FastAPI integration
- Local demo preview that does not call AWS or the backend
- Responsive desktop/tablet/mobile layout

## Run

From this `web-ui` directory:

```powershell
npm install
npm run dev
```

Open the Vite URL shown by the terminal, normally:

```text
http://localhost:5173
```

The frontend expects FastAPI at:

```text
http://127.0.0.1:8000
```

## Demo flow

1. Start Ollama.
2. Start FastAPI.
3. Start this Vite UI.
4. Click **Load Demo** for a zero-risk presentation preview.
5. Open **Human Approval & Remediation**.
6. Keep **Safe Demo Simulation** enabled.
7. Click **Approve & Execute** to demonstrate the approval → remediation → verification experience without modifying AWS.

For a real backend run, use **New Incident**. The request goes to the existing `/incident` endpoint.

## Backend contract used

- `GET /health`
- `POST /incident`
- `POST /incident/{thread_id}/approve`
- `POST /cloudwatch/incidents`
- Optional `GET /incident/{thread_id}` if added to the backend

## Design direction

The UI is intentionally built around an incident command-center pattern instead of a long Streamlit document. The primary object is the active incident, with investigation state, RCA evidence, safety and remediation visible in one workflow.
