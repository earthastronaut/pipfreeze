#!/bin/bash

export PATH=/app/scripts:${PATH}

PIP_VERSIONS_FILE=$1
PIP_VERSIONS_UNSUPPORTED=$2
REQUIREMENTS=$3

VERSIONS=$(cat ${PIP_VERSIONS_FILE} | tr -d '\r')
VERSIONS_UNSUPPORTED=$(cat ${PIP_VERSIONS_UNSUPPORTED} | tr -d '\r')

for version in $VERSIONS
do
    if [[ "${VERSIONS_UNSUPPORTED}" == *"$version"* ]]
    then
        echo "Unsupported version: $version"
        echo $version > /tmp/pip-versions-unsupported.txt
    else
        echo "Checking version $version"
        echo "  run-test-pip-version.sh $REQUIREMENTS $version"
        if $(run-test-pip-version.sh $REQUIREMENTS $version > /tmp/test-output-${version}.txt 2>&1)
        then
            echo "  Supported"
        else
            echo "  !! Unsupported !!"
            echo $version > /tmp/pip-versions-unsupported.txt
        fi
    fi
done
