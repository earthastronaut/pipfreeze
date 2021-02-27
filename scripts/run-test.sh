#!/bin/bash

set -e

REQUIREMENTS=$1

echo "------------------- install --------------------"
pip install -r ${REQUIREMENTS}
echo "------------------------------------------------"

echo "---------------- pip freeze --------------------"
pip freeze | sort > /tmp/test-pip-freeze.txt
cat /tmp/test-pip-freeze.txt
echo "------------------------------------------------"

echo "---------------- pipfreeze ---------------------"
python /app/pipfreeze.py --exclude=pipfreeze > /tmp/test-pipfreeze.txt
cat /tmp/test-pipfreeze.txt
echo "------------------------------------------------"

echo "---------------- uninstall ---------------------"
cat /tmp/test-pip-freeze.txt | xargs pip uninstall -y
echo "------------------------------------------------"

echo "------ reinstall from pipfreeze ----------------"
pip install -r /tmp/test-pipfreeze.txt
echo "------------------------------------------------"

echo "-------- verify from pip freeze ----------------"
pip freeze | sort > /tmp/test2-pip-freeze.txt
diff /tmp/test-pip-freeze.txt /tmp/test2-pip-freeze.txt
echo "------------------------------------------------"

echo "SUCCESS"