# SRE Incident Response Platform — Run Guide

## ⚡ 60-Second Quick Start

If you only need to **show the project to someone**, you do NOT need to read this entire guide.

### 1. Open 4 PowerShell terminals

**Terminal 1 — Project + AWS**

```powershell
cd "D:\Cloudsoft Practice\All_Resource\SRE-Incident-Response-Platform"
.\venv\Scripts\Activate.ps1
$env:AWS_DEFAULT_REGION = "us-east-1"
$env:AWS_REGION = "us-east-1"
aws sts get-caller-identity
```

**Terminal 2 — Ollama**

```powershell
ollama serve
```

**Terminal 3 — FastAPI**

```powershell
cd "D:\Cloudsoft Practice\All_Resource\SRE-Incident-Response-Platform"
.\venv\Scripts\Activate.ps1
$env:AWS_DEFAULT_REGION = "us-east-1"
$env:AWS_REGION = "us-east-1"
uvicorn api.main:app --reload
```

**Terminal 4 — React**

```powershell
cd "D:\Cloudsoft Practice\All_Resource\SRE-Incident-Response-Platform\web-ui"
npm run dev
```

### 2. Open the UI

Open:

```text
http://localhost:5173
```

### 3. Verify the connection

Run in another PowerShell:

```powershell
Invoke-RestMethod "http://localhost:5173/api/health"
```

Expected:

```text
status
------
healthy
```

### 4. For a zero-risk presentation

Click:

```text
Load Demo
```

This is the fastest way to show the React Command Center without starting a new backend incident.

### 5. For the real end-to-end demonstration

Click:

```text
New Incident
```

Use:

```text
Service:
order-api

Incident:
The order-api service is returning HTTP 500 errors and requests are timing out.
```

When Human Approval appears:

```text
Action:
reboot_ec2

Target:
i-0123456789abcdef0

Safe Demo Simulation:
ON
```

Then click:

```text
Approve & Execute
```

Expected final result:

```text
EXECUTED - EC2 REBOOT VERIFIED THROUGH SAFE SIMULATION
VERIFIED
```

**Important:** Keep Safe Demo Simulation ON for portfolio demonstrations. No AWS infrastructure is modified in this mode.

---

# 1. Project Location

Windows project path:

```text
D:\Cloudsoft Practice\All_Resource\SRE-Incident-Response-Platform
```

GitHub repository:

https://github.com/AnirudhPratapShukla/SRE-Incident-Response-Platform

React frontend:

```text
D:\Cloudsoft Practice\All_Resource\SRE-Incident-Response-Platform\web-ui
```

Python virtual environment:

```text
D:\Cloudsoft Practice\All_Resource\SRE-Incident-Response-Platform\venv
```

---

# 2. Architecture

```text
AWS CloudWatch / Manual Incident
            |
            v
      Incident Detection
            |
            v
       Jira Incident
            |
            v
      LangGraph Workflow
            |
    +-------+--------+
    |       |        |
    v       v        v
  Logs   Metrics  Infrastructure
    |       |        |
    +-------+--------+
            |
            v
         AWS MCP
            |
            v
           RAG
            |
            v
           RCA
            |
            v
       Safety Gate
            |
            v
      Human Approval
        /        \
     Reject     Approve
       |           |
      END          v
             Controlled
             Remediation
                  |
                  v
             Verification
                  |
                  v
               Jira DONE
                  |
                  v
             Final Report
```

---

# 3. Four-Terminal Development Setup

## Terminal 1 — AWS Environment

```powershell
cd "D:\Cloudsoft Practice\All_Resource\SRE-Incident-Response-Platform"
.\venv\Scripts\Activate.ps1
$env:AWS_DEFAULT_REGION = "us-east-1"
$env:AWS_REGION = "us-east-1"
aws sts get-caller-identity
```

Keep this terminal open.

## Terminal 2 — Ollama

```powershell
ollama serve
```

The local Ollama service runs on:

```text
127.0.0.1:11434
```

Check installed models:

```powershell
ollama list
```

Current project model:

```text
qwen2.5:3b
```

## Terminal 3 — FastAPI

```powershell
cd "D:\Cloudsoft Practice\All_Resource\SRE-Incident-Response-Platform"
.\venv\Scripts\Activate.ps1
$env:AWS_DEFAULT_REGION = "us-east-1"
$env:AWS_REGION = "us-east-1"
uvicorn api.main:app --reload
```

FastAPI:

```text
http://127.0.0.1:8000
```

## Terminal 4 — React/Vite

```powershell
cd "D:\Cloudsoft Practice\All_Resource\SRE-Incident-Response-Platform\web-ui"
npm install
npm run dev
```

React:

```text
http://localhost:5173
```

---

# 4. Health Checks

## FastAPI

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/health"
```

Expected:

```text
status
------
healthy
```

## React → FastAPI

```powershell
Invoke-RestMethod "http://localhost:5173/api/health"
```

Expected:

```text
status
------
healthy
```

If both are healthy, the frontend/backend connection is working.

---

# 5. React Command Center

Open:

```text
http://localhost:5173
```

Main sections:

- Overview
- Incidents
- AI Investigation
- Remediation
- CloudWatch
- Health Check
- Clear Workspace

---

# 6. Zero-Risk Demo

For a quick presentation:

1. Open the React UI.
2. Click **Load Demo**.
3. Navigate through the dashboard.
4. Show:
   - Incident overview
   - AI investigation
   - RCA/evidence
   - Human approval
   - Remediation
   - Verification
   - CloudWatch

This mode is intended for UI presentation and does not require a new live incident workflow.

---

# 7. Full Live Incident Demo

Click **New Incident**.

Use:

```text
Service:
order-api
```

Incident:

```text
The order-api service is returning HTTP 500 errors and requests are timing out.
```

The workflow progresses through:

```text
Monitoring
    ↓
Logs
    ↓
Infrastructure
    ↓
MCP AWS
    ↓
RAG
    ↓
RCA
    ↓
Safety
    ↓
Jira Review
    ↓
Human Approval
```

---

# 8. Human Approval and Safe Remediation

At the approval screen review:

- Service
- Root cause
- Risk
- Recommendation
- Target instance
- Safety information

For the safe portfolio demo use:

```text
Action:
reboot_ec2
```

Target:

```text
i-0123456789abcdef0
```

Enable:

```text
Safe Demo Simulation
```

Then click:

```text
Approve & Execute
```

Expected:

```text
EXECUTED - EC2 REBOOT VERIFIED THROUGH SAFE SIMULATION
```

and:

```text
VERIFIED
```

The UI should show:

```text
RECOVERY VERIFIED
Service recovery confirmed
```

---

# 9. Jira Lifecycle

The intended Jira lifecycle is:

```text
To Do
  ↓
In Progress
  ↓
In Review
  ↓
Done
```

The workflow uses Jira as the incident lifecycle record.

---

# 10. CloudWatch

Open:

```text
CloudWatch
```

Default region:

```text
us-east-1
```

Click:

```text
Scan CloudWatch
```

The scan is read-only.

If there are no active alarms, a valid response is:

```json
{
  "status": "no_incidents",
  "region": "us-east-1",
  "incidents_detected": 0,
  "incidents": []
}
```

---

# 11. Backend API

Available endpoints:

```text
GET  /health
POST /incident
POST /incident/{thread_id}/approve
POST /cloudwatch/incidents
GET  /incident/{thread_id}
```

Example incident:

```json
{
  "service": "order-api",
  "incident": "The order-api service is returning HTTP 500 errors and requests are timing out."
}
```

Example safe approval:

```json
{
  "decision": "yes",
  "remediation_action": "reboot_ec2",
  "remediation_instance_id": "i-0123456789abcdef0",
  "simulation_mode": true
}
```

---

# 12. Testing

From the project root:

```powershell
cd "D:\Cloudsoft Practice\All_Resource\SRE-Incident-Response-Platform"
.\venv\Scripts\Activate.ps1
```

Targeted backend tests:

```powershell
python -m pytest tests/mcp tests/test_remediation.py tests/test_workflow.py tests/test_rca.py -v
```

API tests:

```powershell
python -m pytest tests/test_api.py tests/test_cloudwatch_api.py -v
```

React production build:

```powershell
cd ".\web-ui"
npm run build
```

---

# 13. Common Problems

## React does not start

```powershell
cd "D:\Cloudsoft Practice\All_Resource\SRE-Incident-Response-Platform\web-ui"
npm install
npm run dev
```

## FastAPI is unavailable

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/health"
```

If it fails, start:

```powershell
uvicorn api.main:app --reload
```

## React says API disconnected

Run:

```powershell
Invoke-RestMethod "http://localhost:5173/api/health"
```

Then:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/health"
```

Both should return `healthy`.

## RCA does not progress

Check Ollama:

```powershell
ollama list
```

Start it if necessary:

```powershell
ollama serve
```

## AWS authentication problem

```powershell
aws sts get-caller-identity
```

Then:

```powershell
$env:AWS_DEFAULT_REGION = "us-east-1"
$env:AWS_REGION = "us-east-1"
```

---

# 14. Stopping the Project

In the React terminal:

```text
Ctrl+C
```

In the FastAPI terminal:

```text
Ctrl+C
```

In the Ollama terminal:

```text
Ctrl+C
```

---

# 15. Safety Rule

For portfolio demonstrations:

```text
Safe Demo Simulation = ON
```

Do not use a real production EC2 instance for demonstrations.

The currently supported controlled remediation action is:

```text
reboot_ec2
```

Safe Demo Simulation is designed to demonstrate the approval, remediation, and verification workflow without modifying AWS infrastructure.

---

# 16. GitHub

Repository:

https://github.com/AnirudhPratapShukla/SRE-Incident-Response-Platform

Current stable release:

```text
v1.0.0
```

React frontend:

```text
web-ui/
```

Project screenshots:

```text
docs/screenshots/
```

---

# 17. Quick Architecture Summary

```text
CloudWatch / Manual Incident
          ↓
        Jira
          ↓
      LangGraph
          ↓
     RAG + RCA
          ↓
     Safety Gate
          ↓
   Human Approval
          ↓
      AWS MCP
          ↓
Controlled Remediation
          ↓
     Verification
          ↓
      Jira DONE
          ↓
 React Command Center
```

---

## Project Status

```text
React Command Center          [x]
FastAPI Backend               [x]
LangGraph Workflow            [x]
Ollama RCA                    [x]
RAG                           [x]
AWS CloudWatch                [x]
AWS MCP                       [x]
Jira Integration              [x]
Safety Gate                   [x]
Human Approval                [x]
Safe Demo Remediation         [x]
Recovery Verification         [x]
GitHub                        [x]
```
