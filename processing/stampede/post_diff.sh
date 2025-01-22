#!/bin/bash
#SBATCH --partition=skx-dev
#SBATCH --time=1:00:00
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

# call final
final=$(echo submit/DEEP/*/allSky/diff_drp/DEEP-DRP/step4a/*/final_job.bash)
dirname -- $final | xargs -P 48 -I % bash %/final_job.bash %/*Z.qgraph $REPO
dirname -- $final | xargs -I % mv %/final_job.bash %/final_job.bash.ran

# call retries
butler query-collections $REPO "DEEP/*/allSky/diff_drp/*" --collection-type RUN | grep RUN | awk '{print $1}' | xargs -P 48 -I % python bin/retries.py $REPO %

cleanup
