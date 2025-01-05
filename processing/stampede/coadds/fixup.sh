#!/usr/bin/env bash
#SBATCH --partition=skx
#SBATCH --time=24:00:00
#SBATCH --nodes=1

# COADD MEDIUM - 150 < n <= 200
# 16GB / core
# SKX 192GB / 48 cores
# 10 cores = 19.2 GB / core

w=$DEEP_PROJECT_DIR
cd $w
source $w/bin/setup.sh

export PROC_LSST_SITE="stampede" #${PROC_LSST_SITE:-"stampede"}
export PROC_LSST_QUEUE="multi" # ${PROC_LSST_QUEUE:-"multi"}
export PROC_LSST_MULTI_QUEUES="local" # ${PROC_LSST_MULTI_QUEUES:-"local,skx"}
export PROC_LSST_NODES_PER_BLOCK="1" #${PROC_LSST_NODES_PER_BLOCK:-1}
export PROC_LSST_CORES_PER_NODE="2" # ${PROC_LSST_CORES_PER_NODE:-48}
export PROC_LSST_MAX_BLOCKS="4" # ${PROC_LSST_MAX_BLOCKS:-1}
export PROC_LSST_WALLTIME="24:00:00"
export J=12



