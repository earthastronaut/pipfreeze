#!/bin/bash

set -e

function pip_versions() {
    set +e
    pip install pip==9 > /dev/null 2>&1
    pip install pip== 2>&1 > /dev/null \
        | grep versions \
        | python -c '
import sys
versions = sys.stdin.readline().strip(")\n").split("versions:")[1].split(",")
for version in versions:
    print(version.strip())
        '
    set -e
}

function reset_pip() {
    curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py && python /tmp/get-pip.py
}

VERSIONS=$(pip_versions)
TEST_COMMAND="$(dirname $0)/run-test.sh $(dirname $0)/../references/py3.8/001-requirements.txt"

while test $# -gt 0; do
  case "$1" in
    # -h|--help)
    #   echo "$package - attempt to capture frames"
    #   echo " "
    #   echo "$package [options] application [arguments]"
    #   echo " "
    #   echo "options:"
    #   echo "-h, --help                show brief help"
    #   echo "-a, --action=ACTION       specify an action to use"
    #   echo "-o, --output-dir=DIR      specify a directory to store output in"
    #   exit 0
    #   ;;
    --version)
      shift
      VERSIONS="$1"
      shift
      ;;
    --test)
      shift
      TEST_COMMAND=$1
      shift
      ;;
    --unsupported)
      shift
      UNSUPPORTED_VERSIONS=$(cat $1)
      shift
      ;;
    *)
      break
      ;;
  esac
done


echo "Pip versions:"
echo "$VERSIONS"
echo "" > /tmp/unsupported-pip-versions.txt

# baseline
reset_pip > /dev/null 2>&1
echo "Baseline:  ${TEST_COMMAND}"
_=$(${TEST_COMMAND})

# check versions
for version in $VERSIONS
do
    if [[ "$UNSUPPORTED_VERSIONS" == *"$version"* ]]
    then
        echo "Unsupported version: $version"
        echo "$version known" >> /tmp/unsupported-pip-versions.txt
    else
        echo "Checking version $version"
        echo "  pip install pip==$version"
        echo "  ${TEST_COMMAND}"
        reset_pip > /dev/null 2>&1
        pip install pip==$version > /dev/null
        if $(${TEST_COMMAND} > /tmp/test-output-${version}.txt 2>&1)
        then
            echo "  Supported"
        else
            echo "  !! Unsupported !!"
            echo $version >> /tmp/unsupported-pip-versions.txt
        fi
    fi
done
