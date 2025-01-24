#!/bin/bash

cd $SCRATCH/DEEP_processing

nights=(
    20190927
    20190928
    20201015
    20201016
    20201017
    20201018
    20201019
    20201020
    20201021
    20210503
    20210504
    20210506
    20210507
    20210509
    20210510
    20210512
)
for night in ${nights[@]}; do
    bash -x ./processing/stampede/copy/copy.sh "DEEP/${night}" 1> ./processing/stampede/copy/$(hostname -a).log 2>&1
done
