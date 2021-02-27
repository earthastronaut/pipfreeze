.PHONY: build build-local test

SHELL=/bin/bash

build:
	./activate.sh
	docker-compose build

test:
	docker-compose up

clean:
	docker-compose down --rmi all --remove-orphans
	rm -rf .venv || true