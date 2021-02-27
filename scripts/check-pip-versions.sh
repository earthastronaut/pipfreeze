#!/bin/bash

export PATH=/app/scripts:${PATH}

PIP_VERSIONS_FILE=$1
REQUIREMENTS=$3

#VERSIONS=$(cat ${PIP_VERSIONS_FILE} | tr -d '\r')
VERSIONS=$(cat ${PIP_VERSIONS_FILE} | tr -d '\r')


cat ${PIP_VERSIONS_FILE} | while read version
do
    script="
assert len('${version}') > 0
assert '#' not in '${version}'
"
    if python -c "$script" 2> /dev/null
    then
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
