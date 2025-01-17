#!/bin/bash

w=$DEEP_PROJECT_DIR
cd $w
source $w/bin/setup.sh

export J="${J:-48}"

runs=$(butler query-collections $REPO --collection-type RUN | grep RUN | awk '{print $1}')
echo "${runs}" | xargs -P ${J} -I % python bin/transfer.py ./repo/% epyc /epyc/data4/stampede_repo/% --exclude "raw" --exclude "*postISRCCD*" --exclude "*icExp*" --exclude "deepCoadd*Warp" --exclude "overscanRaw" --exclude "cpBiasIsrExp" --exclude "cpFlatIsrExp" 1> transfer_$(date +%s).log 2>&1
