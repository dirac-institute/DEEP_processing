#!/usr/bin/env bash
#SBATCH --partition=skx
#SBATCH --time=48:00:00
#SBATCH --nodes=1

w=$DEEP_PROJECT_DIR
cd $w
source $w/bin/setup.sh

export PROC_LSST_SITE="stampede" #${PROC_LSST_SITE:-"stampede"}
export PROC_LSST_QUEUE="multi" # ${PROC_LSST_QUEUE:-"multi"}
export PROC_LSST_MULTI_QUEUES="local,skx" # ${PROC_LSST_MULTI_QUEUES:-"local,skx"}
export PROC_LSST_NODES_PER_BLOCK="1" #${PROC_LSST_NODES_PER_BLOCK:-1}
export PROC_LSST_CORES_PER_NODE="48" # ${PROC_LSST_CORES_PER_NODE:-48}
export PROC_LSST_MAX_BLOCKS="6" # ${PROC_LSST_MAX_BLOCKS:-1}
export J=5 # cores per worker for local
env | grep PROC_LSST

bash $w/processing/stampede/proc.sh python $w/bin/night.py $REPO $w/data/exposures.ecsv --workers 40 "$@" 

