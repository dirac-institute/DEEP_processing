#!/usr/bin/env bash
#SBATCH --partition=skx
#SBATCH --time=48:00:00
#SBATCH --nodes=1

# COADD MEDIUM - 150 < n <= 200
# 16GB / core
# SKX 192GB / 48 cores
# 10 cores = 19.2 GB / core

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

# patches=$(python $w/bin/select_patches.py $w/data/warp_counts_allSky.csv --min 0 --max 50)
# python $w/bin/pipeline.py $REPO coadd allSky --steps assembleCoadd --where "skymap='discrete' and patch in (${patches})"
# python $w/bin/coadd.py $REPO allSky --where "skymap='discrete' and patch in (${patches})"
# subsets=$(python -c 'import sys; print("|".join([f"^{x}$" for x in sys.argv[1:]]))' {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22})

export PROC_LSST_SITE="stampede" #${PROC_LSST_SITE:-"stampede"}
export PROC_LSST_QUEUE="multi" # ${PROC_LSST_QUEUE:-"multi"}
export PROC_LSST_MULTI_QUEUES="skx" # ${PROC_LSST_MULTI_QUEUES:-"local,skx"}
export PROC_LSST_NODES_PER_BLOCK="1" #${PROC_LSST_NODES_PER_BLOCK:-1}
export PROC_LSST_CORES_PER_NODE="16" # ${PROC_LSST_CORES_PER_NODE:-48}
export PROC_LSST_MAX_BLOCKS="20" # ${PROC_LSST_MAX_BLOCKS:-1}
export PROC_LSST_WALLTIME="8:00:00"
export J=16 # cores per worker for local
env | grep PROC_LSST
python $w/bin/pipeline.py $REPO coadd allSky --coadd-subset fixup/0 --steps assembleCoadd &

export PROC_LSST_SITE="stampede" #${PROC_LSST_SITE:-"stampede"}
export PROC_LSST_QUEUE="multi" # ${PROC_LSST_QUEUE:-"multi"}
export PROC_LSST_MULTI_QUEUES="local,skx" # ${PROC_LSST_MULTI_QUEUES:-"local,skx"}
export PROC_LSST_NODES_PER_BLOCK="1" #${PROC_LSST_NODES_PER_BLOCK:-1}
export PROC_LSST_CORES_PER_NODE="4" # ${PROC_LSST_CORES_PER_NODE:-48}
export PROC_LSST_MAX_BLOCKS="20" # ${PROC_LSST_MAX_BLOCKS:-1}
export PROC_LSST_WALLTIME="24:00:00"
export J=4 # cores per worker for local
env | grep PROC_LSST
python $w/bin/pipeline.py $REPO coadd allSky --coadd-subset fixup/1 --steps assembleCoadd &

wait

$w/bin/db_ctl.sh $REPO stop

