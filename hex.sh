#!/bin/bash

m_flag=""
g_flag=false

# check if pdbFiles folder exists and is not empty
if [ ! -d "pdbFiles" ]; then
    echo "pdbFiles folder does not exist"
    exit 1
fi
if [ -z "$(ls -A pdbFiles)" ]; then
    echo "pdbFiles folder is empty"
    exit 1
fi

# check is hex is installed
if ! command -v hex &> /dev/null; then
    echo "hex is not installed"
    exit 1
fi

# check if -m flag is given
if [[ $* != *-m* ]]; then
    echo "-m flag is not given"
    exit 1
fi

while getopts 'm:g' OPTIONS; do
    case "$OPTIONS" in
        m) m_flag="$OPTARG"
            ;;
        g) g_flag=true
            ;;
        ?) echo "script usage: $(basename \$0) [-m <docking method mac file>] [-g]"
            exit 1
            ;;
    esac
done

for file in pdbFiles/*.pdb; do
