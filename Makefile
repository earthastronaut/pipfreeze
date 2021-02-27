.PHONY: build build-local test

SHELL=/bin/bash

build:
	./activate.sh
	docker-compose build

clean:
	docker-compose down --rmi all --remove-orphans
	rm -rf .venv || true
	rm -rf *.egg-info || true
	rm -rf __pycache__ || true

test:
	docker-compose up

bash:
	docker-compose run --rm py bash

pip-versions:
	docker-compose run --rm py3.8 ./scripts/versions.sh pip > references/pip-versions.txt
	cat references/pip-versions.txt

pip-checks:
	docker-compose run --rm py \
		./scripts/check-pip-versions.sh \
		references/py3.8/pip-versions-supported.txt \
		references/py3.8/001-requirements.txt 

	docker-compose run --rm py3.8 \
		./scripts/check-pip-versions.sh \
		references/py3.8/pip-versions-supported.txt \
		references/py3.8/001-requirements.txt 

	docker-compose run --rm py2.7 \
		./scripts/check-pip-versions.sh \
		references/py3.8/pip-versions-supported.txt \
		references/py2.7/001-requirements.txt
