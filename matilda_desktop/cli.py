"""
matilda-desktop — CLI agent.

Usage:
    matilda
    matilda "What is the weather in Paris?"
    matilda --reasoning
"""

import argparse
from pathlib import Path
from uuid import uuid4

from langgraph.types import Command

from .agent import make_agent


# One thread per conversation so the checkpointer can resume after interrupts
THREAD_ID = str(uuid4())
CONFIG = {"configurable": {"thread_id": THREAD_ID}}


def run_question(messages: list, agent: object) -> list:
    stream = agent.stream_events(
        {"messages": messages},
        version="v3",
        config=CONFIG,
    )

    while True:
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

        if not stream.interrupted:
            break

        # Human In The Loop — approve or reject interrupted tool calls
        decisions = []
        for interrupt in stream.interrupts:
            hitl = interrupt.value
            if "action_requests" not in hitl:
                continue
            for req in hitl["action_requests"]:
                name = req["name"]
                args = req["args"]
                print(f"  ⚠️  {name}({args})")
                answer = input("  Approve? [y/N] ").strip().lower()
                if answer in ("y", "yes"):
                    decisions.append({"type": "approve"})
                else:
                    decisions.append({
                        "type": "reject",
                        "message": "User rejected the execution.",
                    })

        if decisions:
            stream = agent.stream_events(
                Command(resume={"decisions": decisions}),
                version="v3",
                config=CONFIG,
            )

    return stream.output["messages"]


def main():
    parser = argparse.ArgumentParser(description="matilda-desktop CLI agent")
    parser.add_argument("question", nargs="*", help="Single question to ask")
    parser.add_argument("--reasoning", "-r", action="store_true",
                        help="Enable thinking/reasoning")
    args = parser.parse_args()

    agent = make_agent(reasoning=args.reasoning, workspace_dir=Path.cwd())
    sep = "─" * 50
    tag = " [reasoning on]" if args.reasoning else ""

    if args.question:
        question = " ".join(args.question)
        print(f"\n  You: {question}{tag}\n{sep}")
        messages = [{"role": "user", "content": question}]
        run_question(messages, agent)
        return

    print(f"matilda-desktop (streaming){tag}. Type 'exit' to quit.\n")
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
