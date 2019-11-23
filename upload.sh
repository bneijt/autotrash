#!/bin/bash
cd "$(dirname "$0")"
rm -rf dist
pipenv run -- python setup.py sdist bdist_wheel
echo "Ready to upload:"
find dist
case $1 in
    prod)
        pipenv run -- python -m twine upload dist/*
        ;;
    test)
        pipenv run -- python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
        ;;
    *)
        echo "Either prod or test"
        exit 1
        ;;
esac

