#!/bin/bash

set -e

export PATH=/app/scripts:${PATH}

REQUIREMENTS=$1
PIP_VERSION=$2

echo "--------- reset pip -------------"
reset-pip.sh > /dev/null 2>&1
if [ "${PIP_VERSION}" != "" ]
then
    echo "--------- pip $PIP_VERSION -------------"
    pip install pip==$PIP_VERSION > /dev/null
fi
run-test.sh $REQUIREMENTS
