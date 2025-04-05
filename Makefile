.PHONY: lint-fix
lint-fix:
	uv run ruff check --select I --fix .
	uv run ruff format
	uv run toml-sort -i pyproject.toml

.PHONY: test
test:
	uv run pytest -vv .

.PHONY: sync
sync:
	uv sync --all-packages