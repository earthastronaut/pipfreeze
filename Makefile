.PHONY: build build-local test

SHELL=/bin/bash
LATEST_TAG=$(shell git describe --abbrev=0 --tags)

# Build distribution
build:
	source activate.sh && python setup.py sdist bdist_wheel

# Clean distribution and other built objects
clean:
	docker-compose down --rmi all --remove-orphans
	rm -rf .venv || true
	rm -rf *.egg-info || true
	rm -rf __pycache__ || true
	rm -rf dist || true
	rm -rf build || true

# Build and run checks
pre-publish: version-check build
	source activate.sh && twine check dist/*
	# source activate.sh && twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	tar tzf dist/pipfreeze-*.tar.gz

# Publish to pypi
publish: pre-publish
	source activate.sh && twine upload dist/*

# Run tests
test:
	docker-compose up

# Run non-trival but simple
start:
	docker-compose run --rm py bash -c "pip install pandas matplotlib && ./pipfreeze.py"

# Run bash shell
bash:
	docker-compose run --rm py bash

# Display version
version:
	@echo ${LATEST_VERSION}

# Validate that git tag version matches code pipfreeze.__version__
version-check:
	source activate.sh && pipfreeze --version && [ "$$(pipfreeze --version)" = "${LATEST_TAG}" ]

# Store and display versions of pip
pip-versions:
	docker-compose run --rm py3.8 ./scripts/versions.sh pip > references/pip-versions.txt
	cat references/pip-versions.txt

# Check compatibility configurations for python version, pip version, and requirements
# TODO: make more explicit to check all different variations. Add as async check.
#   options=[("python3.8", "pip==20.1.0", "001-requirements.txt"), ...]
#   for option in options: check(*option)
#
check-compatibility:
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

# TODO: make these automated
cicd: test version-check
