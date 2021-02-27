#!/bin/bash

if python -c "import sys; assert sys.version_info[0] == 2" 2> /dev/null
then 
    echo "Python 2"
    curl  https://bootstrap.pypa.io/2.7/get-pip.py -o /tmp/get-pip.py
else
    echo "Python 3"
    curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
fi
python /tmp/get-pip.py
