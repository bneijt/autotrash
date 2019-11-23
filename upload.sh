#!/bin/bash
cd "$(dirname "$0")"
rm -rf dist
pipenv run -- python setup.py sdist bdist_wheel
pipenv run -- python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
