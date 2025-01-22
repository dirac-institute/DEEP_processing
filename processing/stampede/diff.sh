#!/usr/bin/env bash
#SBATCH --partition=skx
#SBATCH --time=48:00:00
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

$w/bin/db_ctl.sh $REPO start

export PROC_LSST_SITE="stampede" #${PROC_LSST_SITE:-"stampede"}
export PROC_LSST_QUEUE="multi" # ${PROC_LSST_QUEUE:-"multi"}
export PROC_LSST_MULTI_QUEUES="local,skx" # ${PROC_LSST_MULTI_QUEUES:-"local,skx"}
export PROC_LSST_NODES_PER_BLOCK="2" #${PROC_LSST_NODES_PER_BLOCK:-1}
export PROC_LSST_CORES_PER_NODE="16" # ${PROC_LSST_CORES_PER_NODE:-48}
export PROC_LSST_MAX_BLOCKS="9" # ${PROC_LSST_MAX_BLOCKS:-1}
export PROC_LSST_WALLTIME="12:00:00"
export J=4 # cores per worker for local
env | grep PROC_LSST

set -u
python bin/diff.py $REPO "$1" --coadd-subset allSky --workers 4

cleanup
