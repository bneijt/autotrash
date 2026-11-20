#!/bin/bash
cd "$(dirname "$0")"
rm -rf dist
uv build
echo "Ready to upload:"
find dist
case $1 in
    prod)
        uv publish
        ;;
    test)
        uv publish --publish-url https://test.pypi.org/legacy/
        ;;
    *)
        echo "Either prod or test"
        exit 1
        ;;
esac
