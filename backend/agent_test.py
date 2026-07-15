"""Test: LangChain create_agent + ChatAnthropic (llama.cpp local) + tool calling."""
from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic

# --- Tools ---

def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    return f"The weather in {city} is 22°C and sunny."

# --- Model: llama.cpp via Anthropic-compatible API ---

model = ChatAnthropic(
    base_url="http://localhost:8080",
    api_key="not-needed",
    model="gemma-4-E4B-it-qat",
    temperature=0.7,
    max_tokens=4096,
)

# --- Agent ---

agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="You are a helpful assistant. Use the tools available to answer the user's questions.",
)

# --- Test ---

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in Paris?"}]}
)

print("=== RESULT ===")
for msg in result["messages"]:
    role = msg.type
    content = msg.content
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        print(f"\n[{role}] (tool calls)")
        for tc in msg.tool_calls:
            print(f"  -> {tc['name']}({tc['args']})")
    elif content:
        print(f"\n[{role}]: {content}")
    else:
        print(f"\n[{role}]: (empty / thinking)")
