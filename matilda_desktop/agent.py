from pathlib import Path
import warnings

from langchain_core._api.beta_decorator import LangChainBetaWarning

warnings.filterwarnings("ignore", message=".*is being sunset.*")
warnings.filterwarnings("ignore", category=LangChainBetaWarning)

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend, LocalShellBackend
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from .tools import get_weather, search


# ─── Directories ───────────────────────────────────────────────────────────

MATILDA_HOME = Path.home() / ".matilda"
MATILDA_SKILLS = MATILDA_HOME / "skills"
MATILDA_MEMORY = MATILDA_HOME / "memory"


def ensure_dirs():
    for d in [MATILDA_SKILLS, MATILDA_MEMORY]:
        d.mkdir(parents=True, exist_ok=True)


# ─── Backend ──────────────────────────────────────────────────────────────
#
# CompositeBackend routes:
#   /skills/ → ~/.matilda/skills/   (persistent skill definitions)
#   /memory/ → ~/.matilda/memory/   (long-term agent memories)
#   default  → LocalShellBackend(workspace_dir)  (project dir, execute OK)
#
# execute is available because LocalShellBackend implements SandboxBackendProtocol.
# Human In The Loop via interrupt_on={"execute": True} pauses before running.
# MemorySaver checkpointer preserves state across the interrupt/resume cycle.

def make_backend(workspace_dir: str | Path) -> CompositeBackend:
    ensure_dirs()
    workspace_dir = Path(workspace_dir).resolve()
    return CompositeBackend(
        default=LocalShellBackend(
            root_dir=str(workspace_dir),
            virtual_mode=True,
            inherit_env=True,
        ),
        routes={
            "/skills/": FilesystemBackend(
                root_dir=str(MATILDA_SKILLS), virtual_mode=True,
            ),
            "/memory/": FilesystemBackend(
                root_dir=str(MATILDA_MEMORY), virtual_mode=True,
            ),
        },
    )


# ─── Model ────────────────────────────────────────────────────────────────

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


# ─── Agent ────────────────────────────────────────────────────────────────

def make_agent(reasoning: bool = False, workspace_dir: str | Path | None = None):
    model = make_model(reasoning=reasoning)
    if workspace_dir is None:
        workspace_dir = Path.cwd()
    return create_deep_agent(
        model=model,
        tools=[get_weather, search],
        system_prompt=(
            "You are a helpful assistant. Use the tools available to answer the "
            "user's questions. Be concise."
        ),
        backend=make_backend(workspace_dir),
        interrupt_on={"execute": True},
        checkpointer=MemorySaver(),
    )
