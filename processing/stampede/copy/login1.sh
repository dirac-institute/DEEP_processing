#!/bin/bash

cd $SCRATCH/DEEP_processing

nights=(
    20190401
    20190402
    20190403
    20190504
    20190505
    20190507
    20190601
    20190602
    20190603
    20190706
    20190707
    20190708
    20190827
    20190828
    20190829
    20190926
    "allSky"
)
for night in ${nights[@]}; do
    bash -x ./processing/stampede/copy/copy.sh "DEEP/${night}" 1> "./processing/stampede/copy/$(hostname -a).log" 2>&1
done
