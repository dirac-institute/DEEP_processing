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
export PROC_LSST_MULTI_QUEUES="local,skx" # ${PROC_LSST_MULTI_QUEUES:-"local,skx"}
export PROC_LSST_NODES_PER_BLOCK="1" #${PROC_LSST_NODES_PER_BLOCK:-1}
export PROC_LSST_CORES_PER_NODE="16" # ${PROC_LSST_CORES_PER_NODE:-48}
export PROC_LSST_MAX_BLOCKS="4" # ${PROC_LSST_MAX_BLOCKS:-1}
export PROC_LSST_WALLTIME="8:00:00"
export J=1 # cores per worker for local
env | grep PROC_LSST

function cleanup() {
    $w/bin/db_ctl.sh $w/repo stop
}

trap cleanup SIGINT
trap cleanup SIGTERM
trap cleanup SIGEXIT

$w/bin/db_ctl.sh $REPO start

# patches=$(python $w/bin/select_patches.py $w/data/warp_counts_allSky.csv --min 0 --max 50)
# python $w/bin/pipeline.py $REPO coadd allSky --steps assembleCoadd --where "skymap='discrete' and patch in (${patches})"
# python $w/bin/coadd.py $REPO allSky --where "skymap='discrete' and patch in (${patches})"
subsets=$(python -c 'import sys; print("|".join([f"^{x}$" for x in sys.argv[1:]]))' {23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56})
python $w/bin/coadd_subsets.py $REPO allSky/fixup $w/data/coadd_fixup/warp_subsets --subsets "${subsets}" --workers 4

$w/bin/db_ctl.sh $REPO stop


