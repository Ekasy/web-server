#!/bin/bash

dir="http-test-suite"
host=$1
port=$2

if [ -d "$dir" ]; then
    rm -rf $dir
fi

if ! [ -d "$dir" ]; then
    git clone https://github.com/init/http-test-suite.git
fi

cd $dir

python3 ./httptest.py $host $port
