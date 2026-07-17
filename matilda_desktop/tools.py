from langchain_community.tools import DuckDuckGoSearchRun


def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    return f"The weather in {city} is 22°C and sunny."


search = DuckDuckGoSearchRun()
