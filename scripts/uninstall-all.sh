#!/bin/bash
set -e
pip freeze | xargs pip uninstall -y
