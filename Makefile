.PHONY: run docker test clean

# Run locally (no Docker)
run:
	pip install -r requirements.txt
	streamlit run app/main.py

# Run via Docker
docker:
	docker compose up --build

# Run tests
test:
	pip install pytest
	pytest tests/ -v

# Clear cached data
clean:
	rm -rf data/cache/*
