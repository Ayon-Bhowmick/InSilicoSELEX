#!/bin/bash

r_flag=false
h_flag=false

if [ ! -d "pdbFiles" ]; then
    mkdir pdbFiles
fi

while getopts 'rhc' OPTIONS; do
    case "$OPTIONS" in
        r) # run RNAComposer
            r_flag=true
            ;;
        h) # run hex
            h_flag=true
            ;;
        c) # clean up
            rm -rf pdbFiles
            cd RNAComposer
            rm -rf RNAComposer.log name_directory.pkl errorFiles
            cd ..
            ;;
        ?) echo "script usage: $(basename \$0) [-r] [-h]"
            ;;
    esac
done

if $r_flag; then
    cd RNAComposer
    if [ -z "$(ls | grep RNAComposer.py)" ]; then
        echo "RNAComposer.py not found"
        exit 1
    fi
    echo "running RNAComposer"
    python -u RNAComposer.py > RNAComposer.log
    cd ..
fi

if $h_flag; then
    if [ -z "$(ls | grep hex.sh)" ]; then
        echo "hex.sh not found"
        exit 1
    fi
    read -p "Enter ligand file: " ligand
    read -p "Enter docking method macro file: " macro
    while true; do
        read -p "Use GPU? (y/n): " yn
        case $yn in
            [Yy]*)
                echo "running hex with GPU"
                ./hex.sh -m $macro -l $ligand -g; break
                    ;;
            [Nn]*)
                echo "running hex without GPU"
                ./hex.sh -m $macro -l $ligand; break
                    ;;
            *) echo "Please answer y or n.";;
        esac
    done
fi
