#!/bin/bash
#SBATCH --partition=skx-dev
#SBATCH --time=2:00:00
#SBATCH --nodes=1

w=$DEEP_PROJECT_DIR
cd $w
source $w/bin/setup.sh

function cleanup() {
    $w/bin/db_ctl.sh $w/repo stop
}

trap cleanup SIGINT
trap cleanup SIGTERM
trap cleanup EXIT

./bin/db_ctl.sh ./repo start

set -u

prefix=$1
runs=$(butler query-collections $REPO --collection-type RUN | grep RUN | awk '{print $1}')
echo "$runs" | xargs -P 48 -I % mkdir -p ${prefix}/%
echo "$runs" | xargs -P 40 -I % python bin/size.py $REPO "*" --agg --collections % --output ${prefix}/%/size.csv & 
echo "$runs" | xargs -P 40 -I % python bin/metadata.py $REPO --collections % --output ${prefix}/%/metadata.csv &
wait

cleanup
