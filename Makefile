.PHONY: up down restart ps logs pull \
        curl-text curl-thinking curl-image curl-anthropic curl-health curl-models \
        matilda matilda-reasoning matilda-ask

# ─── Container lifecycle ───────────────────────────────────────────────────

up:
	docker compose -f docker/docker-compose.yml up -d

down:
	docker compose -f docker/docker-compose.yml down

restart:
	docker compose -f docker/docker-compose.yml restart

ps:
	docker compose -f docker/docker-compose.yml ps

logs:
	docker compose -f docker/docker-compose.yml logs -f

pull:
	docker compose -f docker/docker-compose.yml pull

# ─── Test the model ────────────────────────────────────────────────────────

MODEL = gemma-4-E4B-it-qat
API   = http://localhost:8080

curl-text:
	curl -s $(API)/v1/chat/completions \
		-H "Content-Type: application/json" \
		-d '{"model": "$(MODEL)", "messages": [{"role": "user", "content": "What is the capital of France?"}], "stream": false, "max_tokens": 128}' | python3 -m json.tool

curl-thinking:
	curl -s $(API)/v1/chat/completions \
		-H "Content-Type: application/json" \
		-d '{"model": "$(MODEL)", "messages": [{"role": "user", "content": "What is 37 * 482? Show your reasoning step by step."}], "stream": false, "max_tokens": 512}' | python3 -m json.tool

curl-image:
	@if [ -z "$(IMG)" ]; then \
		echo "Usage: make curl-image IMG=path/to/image.jpg"; \
		exit 1; \
	fi
	@echo "Encoding image to base64..."
	BASE64=$$(base64 -w0 "$(IMG)"); \
	EXT=$$(echo "$(IMG)" | sed 's/.*\.//'); \
	MIME="image/$$EXT"; \
	[ "$$EXT" = "jpg" ] && MIME="image/jpeg"; \
	curl -s $(API)/v1/chat/completions \
		-H "Content-Type: application/json" \
		-d "{\"model\": \"$(MODEL)\", \"messages\": [{\"role\": \"user\", \"content\": [{\"type\": \"text\", \"text\": \"Describe this image in detail.\"}, {\"type\": \"image_url\", \"image_url\": {\"url\": \"data:$$MIME;base64,$$BASE64\"}}]}], \"stream\": false, \"max_tokens\": 512}" | python3 -m json.tool

curl-anthropic:
	curl -s $(API)/v1/messages \
		-H "Content-Type: application/json" \
		-H "x-api-key: borrelle" \
		-H "anthropic-version: 2023-06-01" \
		-d '{"model": "$(MODEL)", "max_tokens": 256, "messages": [{"role": "user", "content": "What is the capital of France?"}]}' | python3 -m json.tool

curl-health:
	curl -s $(API)/health | python3 -m json.tool

curl-models:
	curl -s $(API)/v1/models | python3 -m json.tool

# ─── Tauri desktop ───────────────────────────────────────────────────────────

tauri-dev:
	npm run tauri dev

tauri-build:
	npm run tauri build

# ─── matilda CLI ───────────────────────────────────────────────────────────

VENV = .venv

# Interactive REPL mode
matilda:
	$(VENV)/bin/python -m matilda_desktop.cli
matilda-reasoning:
	$(VENV)/bin/python -m matilda_desktop.cli --reasoning

# Single question: make matilda-ask Q="your question here"
matilda-ask:
	@if [ -z "$(Q)" ]; then \
		echo "Usage: make matilda-ask Q=\"your question here\""; \
		exit 1; \
	fi
	$(VENV)/bin/python -m matilda_desktop.cli "$(Q)"
matilda-ask-r:
	@if [ -z "$(Q)" ]; then \
		echo "Usage: make matilda-ask-r Q=\"your question here\""; \
		exit 1; \
	fi
	$(VENV)/bin/python -m matilda_desktop.cli --reasoning "$(Q)"
