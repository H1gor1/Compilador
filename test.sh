#!/bin/bash

function run_tests(){
    for test in $(ls tests/*.txt); do
        echo "Running test $test"
        python3 main.py -sc $test -o $(echo $test | sed 's/.txt/.py/' )
        echo "Test $test done"
    done
}

run_tests