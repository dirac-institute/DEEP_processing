#!/usr/bin/env bash
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
trap cleanup SIGEXIT

./bin/db_ctl.sh ./repo start


dirname -- $@ | xargs -P 48 -I % bash %/final_job.bash %/*Z.qgraph $REPO

cleanup


