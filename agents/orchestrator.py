from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain.agents import create_agent

from tools.metrics import get_metrics
from tools.logs import get_logs
from tools.rag import search_historical_incidents


load_dotenv()


llm = ChatOllama(
    model="qwen2.5:3b"
)


SYSTEM_PROMPT = """
You are an SRE Incident Investigation Agent.

Your job is to investigate production incidents using:

1. Metrics
2. Logs
3. Historical incidents (RAG)

Investigation Workflow:

Step 1:
Identify the affected service.

Step 2:
Use get_metrics() to inspect:
- CPU
- Memory
- Latency
- Error Rate

Step 3:
Use get_logs() to inspect recent errors.

Step 4:
Use search_historical_incidents() to find
similar past incidents.

Step 5:
Compare:
- Current metrics
- Current logs
- Historical incidents

Step 6:
Identify:
- Most likely root cause
- Supporting evidence
- Similar historical incidents

Step 7:
Provide:
- Root Cause Analysis
- Recommended Fix
- Prevention Recommendations

Always use available tools before answering.

Do not skip historical incident analysis when
investigating production incidents.
"""


agent = create_agent(
    model=llm,
    tools=[
        get_metrics,
        get_logs,
        search_historical_incidents
    ],
    system_prompt=SYSTEM_PROMPT,
)


if __name__ == "__main__":

    question = input("You: ")

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        }
    )

    print("\nSRE Agent:")
    print(result["messages"][-1].content)