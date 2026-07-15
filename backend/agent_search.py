"""Agent with DuckDuckGo search + tool calling via local llama.cpp."""
from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun

# --- Tools ---

def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    return f"The weather in {city} is 22°C and sunny."

search = DuckDuckGoSearchRun()

# --- Model ---

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
    tools=[get_weather, search],
    system_prompt="You are a helpful assistant. Use the tools available to answer the user's questions.",
)

# --- Test ---

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Quelle est la météo à Paris et quelles sont les dernières actualités sur l'IA ?"}]}
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
        print(f"\n[{role}]: {content[:500]}")
    else:
        print(f"\n[{role}]: (empty / thinking)")
