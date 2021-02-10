#!/bin/bash

set -e

DIR=$(dirname $0)
OUTDIR=${DIR}/output

mkdir -p ${OUTDIR}

pip install -e ${DIR}/..

pip install -r ${DIR}/001_requirements_freeze.txt

pip freeze > ${OUTDIR}/001_requirements_freeze.txt
pipfreeze > ${OUTDIR}/001_requirements_pipfreeze.txt

echo "------------------- freeze --------------------"
cat ${OUTDIR}/001_requirements_freeze.txt
echo "------------------------------------------------"

echo "------------------ pipfreeze ------------------"
cat ${OUTDIR}/001_requirements_pipfreeze.txt
echo "------------------------------------------------"

echo "--------------------  diff  --------------------"
diff ${OUTDIR}/001_requirements_pipfreeze.txt ${DIR}/001_requirements_pipfreeze.txt
echo "------------------------------------------------"
echo "SUCCESS"
