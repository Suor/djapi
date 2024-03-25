#!/usr/bin/bash

set -ex

NAME=djapi
VERSION=`cat VERSION`

echo "Publishing $NAME-$VERSION..."
python setup.py sdist bdist_wheel
twine check dist/$NAME-$VERSION*
twine upload --skip-existing -uSuor dist/$NAME-$VERSION*
