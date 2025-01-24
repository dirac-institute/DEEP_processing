#!/bin/bash

cd $SCRATCH/DEEP_processing

nights=(
    20211001
    20211002
    20211003
    20211004
    20211005
    20211006
    20220525
    20220526
    20220527
    20220528
    20220821
    20220822
    20220823
    20220825
    20220826
    20220827
)
for night in ${nights[@]}; do
    bash -x ./processing/stampede/copy/copy.sh "DEEP/${night}" 1> ./processing/stampede/copy/$(hostname -a).log 2>&1
done
