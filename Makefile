.PHONY: build build-local test

build-local:
	python3 -m venv .venv
	pip install --upgrade pip setuptools
	pip install -e .

test:
	docker-compose up

clean:
	docker-compose down --remove-orphans
