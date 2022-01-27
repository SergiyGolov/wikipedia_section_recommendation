#! /bin/bash

if [ $(mongo 127.0.0.1:27017 --eval 'db.getMongo().getDBNames().indexOf("wikipedia")' --quiet) -lt 0 ]; then
    echo "DB does not exists, importing..."
    mongorestore /dump
else
    echo "DB already exists, no need to import"
fi