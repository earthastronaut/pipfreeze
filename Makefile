.PHONY: build build-local test

SHELL=/bin/bash
LATEST_TAG=$(shell git describe --abbrev=0 --tags)

build:
	source activate.sh && python setup.py sdist bdist_wheel

clean:
	docker-compose down --rmi all --remove-orphans
	rm -rf .venv || true
	rm -rf *.egg-info || true
	rm -rf __pycache__ || true
	rm -rf dist || true
	rm -rf build || true

pre-publish: version-check build
	source activate.sh && twine check dist/*
	# source activate.sh && twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	tar tzf dist/pipfreeze-*.tar.gz

publish: pre-publish
	source activate.sh && twine upload dist/*

test:
	docker-compose up

bash:
	docker-compose run --rm py bash

version:
	@echo ${LATEST_VERSION}

version-check:
	source activate.sh && pipfreeze --version && [ "$$(pipfreeze --version)" = "${LATEST_TAG}" ]

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

cicd: test version-check
