# Matilda Desktop — Project Guide

## Structure

```
matilda-desktop/
├── matilda_desktop/    # Python package (agent backend)
├── src-tauri/          # Tauri / Rust backend
├── src/                # React / TypeScript frontend
├── docker/             # Docker compose for llama.cpp
├── .venv/              # Python virtual env
```

## Commands

### Python agent (CLI)
```bash
make matilda                # interactive REPL
make matilda-ask Q="..."    # single question
```

### Desktop (Tauri)
```bash
make tauri-dev              # dev mode (hot reload)
make tauri-build            # production build
```

### Docker (model server)
```bash
make up                     # start llama.cpp with Gemma 4
make down                   # stop
make logs                   # tail logs
```

## Key Files

- `matilda_desktop/agent.py` — DeepAgent with CompositeBackend (local shell + skills + memory)
- `matilda_desktop/cli.py` — CLI entry point
- `matilda_desktop/tools.py` — tools registered with the agent
- `matilda_desktop/__init__.py` — package init

## Project Type

Python + Rust (Tauri) + React + TypeScript monorepo.
Package name: `matilda-desktop`, Python module: `matilda_desktop`.
