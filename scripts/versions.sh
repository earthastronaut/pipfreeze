#!/bin/bash

PACKAGE=$1

pip install pip==9 > /dev/null 2>&1
pip install ${PACKAGE}== 2>&1 > /dev/null \
    | grep versions \
    | python -c '
import sys
version_content = sys.stdin.readline().strip(")\n").split("versions:")
if len(version_content) <= 1:
    sys.exit()
for version in version_content[1].split(",")[::-1]:
    print(version.strip())
'
