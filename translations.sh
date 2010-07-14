#!/bin/sh

cd po
echo "Generating template"
intltool-update -p -x -g jobs-admin
for p in *.po; do
    echo "Updating $p"
    msgmerge -U --no-wrap -N $p jobs-admin.pot 
done

