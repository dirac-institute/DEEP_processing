#!/usr/bin/env bash
#SBATCH --partition=skx-dev
#SBATCH --time=00:15:00
#SBATCH --nodes=1

w=$SCRATCH/DEEP3

function cleanup() {
    $w/bin/db_ctl.sh $w/repo stop
}

trap cleanup SIGINT
trap cleanup SIGTERM

cd $w
source ./bin/setup.sh

export PROC_LSST_SITE="stampede" #${PROC_LSST_SITE:-"stampede"}
export PROC_LSST_QUEUE="multi" # ${PROC_LSST_QUEUE:-"multi"}
export PROC_LSST_MULTI_QUEUES="local,skx" # ${PROC_LSST_MULTI_QUEUES:-"local,skx"}
export PROC_LSST_NODES_PER_BLOCK="1" #${PROC_LSST_NODES_PER_BLOCK:-1}
export PROC_LSST_CORES_PER_NODE="48" # ${PROC_LSST_CORES_PER_NODE:-48}
export PROC_LSST_MAX_BLOCKS="1" # ${PROC_LSST_MAX_BLOCKS:-1}
export J=${J:-40}
./bin/db_ctl.sh ./repo start
# python $w/bin/night.py ./repo ./data/exposures.ecsv --nights "20190401|20190402" --workers 2
$@
./bin/db_ctl.sh ./repo stop

