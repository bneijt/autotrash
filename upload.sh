#!/bin/bash
cd "$(dirname "$0")"
rm -rf dist
pipenv run -- python setup.py sdist bdist_wheel
case $1 in
    prod)
        pipenv run -- python -m twine upload
        ;;
    test)
        pipenv run -- python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
        ;;
    *)
        echo "Either prod or test"
        exit 1
        ;;
esac

