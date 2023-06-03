#!/bin/bash

r_flag=false
h_flag=false

if [ ! -d "pdbFiles" ]; then
    mkdir pdbFiles
fi

while getopts 'rh' OPTIONS; do
    case “$OPTIONS” in
        r) r_flag=true
            ;;
        h) h_flag=true
            ;;
        ?) echo "script usage: $(basename \$0) [-r] [-h]"
            ;;
    esac
done

if [ r_flag ]; then
    if [ -z “$(ls | grep RNAComposer.py)” ]; then
        echo "RNAComposer.py not found"
        exit 1
    fi
    python RNAComposer.py
fi

if [ h_flag ]; then
    if [ -z “$(ls | grep hex.sh)” ]; then
        echo "hex.sh not found"
        exit 1
    fi
    ./hex.sh
fi
