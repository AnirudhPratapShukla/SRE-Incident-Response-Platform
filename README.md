# SRE Multi-Agent

AI-powered multi-agent SRE incident response system for investigating production incidents, performing root-cause analysis, retrieving historical incidents using RAG, validating remediation safety, and requiring human approval before controlled remediation.

---

## Overview

SRE Multi-Agent combines multiple specialized AI agents into an incident investigation workflow.

Instead of relying on a single LLM response, the system separates responsibilities across monitoring, log analysis, infrastructure analysis, RAG-based historical incident retrieval, root-cause analysis, safety validation, human approval, and remediation planning.

The current v1.0 implementation is designed as a controlled SRE investigation platform.

It does **not** automatically make destructive production changes.

---

## Architecture

```text
                         Incident / Alert
                               |
                               v
                      +-------------------+
                      |    Orchestrator    |
                      +---------+---------+
                                |
             +------------------+------------------+
             |                  |                  |
             v                  v                  v
      +-------------+    +-------------+    +----------------+
      |  Monitoring |    |     Log     |    | Infrastructure |
      |    Agent    |    |    Agent    |    |     Agent      |
      +------+------+    +------+------+    +-------+--------+
             |                  |                    |
             +------------------+--------------------+
                                |
                                v
                         +-------------+
                         |  RAG Agent  |
                         +------+------+
                                |
                                v
                         +-------------+
                         |  RCA Agent  |
                         +------+------+
                                |
                                v
                       +----------------+
                       |  Safety Agent  |
                       +-------+--------+
                               |
                               v
                      +------------------+
                      | Human Approval   |
                      +--------+---------+
                               |
                    +----------+----------+
                    |                     |
                 Approved               Rejected
                    |                     |
                    v                     v
           +------------------+          END
           | Remediation Agent|
           +--------+---------+
                    |
                    v
              Final Report