#!/bin/sh

cd po
echo "Generating template"
intltool-update -p -g jobs-admin
for p in *.po; do
    echo "Merging $p"
    msgmerge -U --no-wrap -N $p jobs-admin.pot 
done
