#!/bin/bash

ROOT_PATH=$(git rev-parse --show-toplevel)
ENV_PATH=${ROOT_PATH}/.venv

# activate virtual environment
if [ -d "${ENV_PATH}" ] 
then
    echo "Found virtual environment ${ENV_PATH}"
    source ${ENV_PATH}/bin/activate
else
    echo "Create python virtual environment ${ENV_PATH}"
    python3 -m venv ${ENV_PATH}
    source ${ENV_PATH}/bin/activate
    pip3 install --upgrade pip setuptools
    pip3 install -e .
fi
