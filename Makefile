.PHONY: install dev test lint clean

install:
	uv sync --all-extras
	uv pip install -e .

dev: install
	uv run ruff check src/ tests/
	uv run pytest tests/ -q

test:
	uv run pytest tests/ -q

lint:
	uv run ruff check src/ tests/ --fix

clean:
	rm -rf .venv
	uv sync --all-extras
	uv pip install -e .
