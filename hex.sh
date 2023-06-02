#!/bin/bash

m_flag=""
g_flag="-nocuda"
receptor=""

# check if pdbFiles folder exists and is not empty
if [ ! -d "pdbFiles" ]; then
    echo "pdbFiles folder does not exist"
    exit 1
fi
if [ -z "$(ls -A pdbFiles)" ]; then
    echo "pdbFiles folder is empty"
    exit 1
fi

if [ ! -d "resultLogs" ]; then
    mkdir resultLogs
fi

# check is hex is installed
if ! command -v hex &> /dev/null; then
    echo "hex is not installed"
    exit 1
fi

# check if -m and -r flags is given
if [[ $* != *-m* ]]; then
    echo "-m flag is not given"
    exit 1
fi
if [[ $* != *-r* ]]; then
    echo "-r flag is not given"
    exit 1
fi

# parse flags
while getopts 'm:gr:' OPTIONS; do
    case "$OPTIONS" in
        m) m_flag="$OPTARG"
            ;;
        g) g_flag="-cuda"
            ;;
        r) receptor="$OPTARG"
            ;;
        ?) echo "script usage: $(basename \$0) [-m <docking method macro file>] [-r <receptor file>] {-g}"
            exit 1
            ;;
    esac
done

for file in pdbFiles/*.pdb; do
    echo "Processing $file"
    hex $g_flag $receptor $file -e $m_flag -l resultLogs/$file.log
done
