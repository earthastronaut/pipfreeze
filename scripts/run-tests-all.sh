#!/bin/bash

set -e

QUERY=$1

for requirements_file in $(ls ${QUERY})
do
    echo "###################################################"
    echo "$(dirname $0)/run-test.sh $requirements_file"
    $(dirname $0)/run-test.sh $requirements_file
done

