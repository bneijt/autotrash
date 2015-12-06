#!/bin/bash
set -e
if [ ! -d "virtualenv" ]; then
    virtualenv -p `which python3` virtualenv
fi

. virtualenv/bin/activate
pip install nose
pip install .
echo '. virtualenv/bin/activate'

