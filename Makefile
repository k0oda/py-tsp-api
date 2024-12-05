run:
	fastapi dev app/main.py
install:
	python -m venv .venv
	source .venv/bin/activate
	pip install -r requirements.txt
lint:
	ruff check --fix
