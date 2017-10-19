#!/usr/bin/env bash

set -e # Exit whenever a command fails
set -x # Output commands run to see them in the Travis interface

if [ "$TEST" == "lint" ]; then
    flake8
    2to3 --fix=asserts --fix=import temba/ 2>&1 #| grep "RefactoringTool: No files need to be modified."
elif [ "$TEST" == "migrations" ]; then
    python manage.py makemigrations --dry-run | grep 'No changes detected' || (echo 'There are changes which require migrations.' && exit 1)
elif [ "$TEST" == "build" ]; then
    python manage.py collectstatic --noinput
    (! python manage.py compress --extension=".haml" --settings=temba.settings_travis | grep 'Error') || exit 1
    node_modules/karma/bin/karma start karma.conf.coffee --single-run --browsers PhantomJS
    coverage run manage.py test --noinput --verbosity=2
else
    echo "The environment variable TEST was not set correctly"
    exit 1
fi
