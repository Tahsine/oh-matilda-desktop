"""
Interactive CLI agent with streaming support.

Usage:
    backend/.venv/bin/python backend/agent_cli.py
    backend/.venv/bin/python backend/agent_cli.py "What is the weather in Paris?"
    backend/.venv/bin/python backend/agent_cli.py --reasoning
"""

import argparse
import sys
import warnings

from langchain_core._api.beta_decorator import LangChainBetaWarning

warnings.filterwarnings("ignore", message=".*is being sunset.*")
warnings.filterwarnings("ignore", category=LangChainBetaWarning)

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun


# ─── Tools ───────────────────────────────────────────────────────────────────

def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    return f"The weather in {city} is 22°C and sunny."

search = DuckDuckGoSearchRun()


# ─── Model ───────────────────────────────────────────────────────────────────

def make_model(reasoning: bool = False):
    kwargs = dict(
        base_url="http://localhost:8080",
        api_key="not-needed",
        model="gemma-4-E4B-it-qat",
        temperature=0.7,
    )
    if reasoning:
        kwargs["thinking"] = {"type": "enabled", "budget_tokens": 1024}
    return ChatAnthropic(**kwargs)


# ─── Agent ───────────────────────────────────────────────────────────────────

def make_agent(reasoning: bool = False):
    model = make_model(reasoning=reasoning)
    return create_agent(
        model=model,
        tools=[get_weather, search],
        system_prompt=(
            "You are a helpful assistant. Use the tools available to answer the "
            "user's questions. Be concise."
        ),
    )


# ─── Streaming runner ────────────────────────────────────────────────────────

def run_question(messages: list, agent: object) -> list:
    """Run a question and stream results. Returns updated messages."""
    stream = agent.stream_events(
        {"messages": messages},
        version="v3",
    )

    for kind, item in stream.interleave("messages", "tool_calls"):
        if kind == "messages":
            for token in item.text:
                print(token, end="", flush=True)
        elif kind == "tool_calls":
            print(f"\n  🔧 {item.tool_name}({item.input})", end="", flush=True)
            for delta in item.output_deltas:
                print(delta, end="", flush=True)
            if item.error:
                print(f"\n  ❌ {item.error}", flush=True)
            else:
                out = item.output
                text = str(out.content) if hasattr(out, "content") else str(out)
                print(f"\n  ✅ {text[:200]}", flush=True)

    print()
    return stream.output["messages"]


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Agent CLI with streaming")
    parser.add_argument("question", nargs="*", help="Single question to ask")
    parser.add_argument("--reasoning", "-r", action="store_true",
                        help="Enable thinking/reasoning")
    args = parser.parse_args()

    agent = make_agent(reasoning=args.reasoning)
    sep = "─" * 50
    tag = " [reasoning on]" if args.reasoning else ""

    if args.question:
        question = " ".join(args.question)
        print(f"\n  You: {question}{tag}\n{sep}")
        messages = [{"role": "user", "content": question}]
        run_question(messages, agent)
        return

    print(f"Agent CLI (streaming){tag}. Type 'exit' to quit.\n")
    messages = []
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            break
        messages.append({"role": "user", "content": question})
        print(sep)
        messages = run_question(messages, agent)


if __name__ == "__main__":
    main()
