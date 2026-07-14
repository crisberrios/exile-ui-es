.PHONY: install test pull translate patch apply bundle revert clean

install:
	uv sync

test:
	uv run pytest -v

pull:
	uv run exile-ui-es pull

translate:
	uv run exile-ui-es translate

patch:
	uv run exile-ui-es patch

apply:
	uv run exile-ui-es apply --install $(INSTALL)

bundle:
	uv run exile-ui-es bundle

revert:
	uv run exile-ui-es revert --install $(INSTALL)

clean:
	rm -rf downloads/ data/spanish/ data/patches/ .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true