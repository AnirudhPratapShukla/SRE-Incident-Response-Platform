# SRE Incident Response Platform

AI-powered SRE incident investigation and controlled remediation platform built with **LangGraph, FastAPI, Ollama, RAG, AWS CloudWatch, AWS MCP, Jira, and React/Vite**.

The platform is designed around a human-in-the-loop incident response workflow that investigates incidents, gathers evidence, performs root-cause analysis, validates remediation safety, requests explicit operator approval, performs controlled remediation, and verifies recovery.

---

## Architecture

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
    Logs   Metrics   Infrastructure
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
       Jira IN REVIEW
              |
              v
       Human Approval
          /       \
       Reject    Approve
         |          |
        END         v
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