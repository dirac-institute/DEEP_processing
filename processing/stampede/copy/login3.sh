#!/bin/bash

cd $SCRATCH/DEEP_processing

nights=(
    20210513
    20210515
    20210516
    20210518
    20210903
    20210904
    20210905
    20210906
    20210907
    20210908
    20210909
    20210910
    20210912
    20210927
    20210928
    20210930
)
for night in ${nights[@]}; do
    bash -x ./processing/stampede/copy/copy.sh "DEEP/${night}" 1> ./processing/stampede/copy/$(hostname -a).log 2>&1
done
