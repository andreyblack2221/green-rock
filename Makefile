.PHONY: venv install run test clean build

venv:
	python3 -m venv .venv

install: venv
	.venv/bin/pip install -r requirements.txt

run:
	.venv/bin/streamlit run app.py

test:
	.venv/bin/pytest tests/

clean:
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rv {} +

build:
	docker-compose build
