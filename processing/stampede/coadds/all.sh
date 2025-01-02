#!/usr/bin/env bash
#SBATCH --partition=skx-dev
#SBATCH --time=2:00:00
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
export PROC_LSST_MULTI_QUEUES="skx" # ${PROC_LSST_MULTI_QUEUES:-"local,skx"}
export PROC_LSST_NODES_PER_BLOCK="1" #${PROC_LSST_NODES_PER_BLOCK:-1}
export PROC_LSST_CORES_PER_NODE="16" # ${PROC_LSST_CORES_PER_NODE:-48}
export PROC_LSST_MAX_BLOCKS="4" # ${PROC_LSST_MAX_BLOCKS:-1}
export PROC_LSST_WALLTIME="12:00:00"
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
python $w/bin/coadd_subsets.py $REPO allSky $w/data/warp_subsets --subsets ".*" --workers 48 
# '^39$|^40$|^41$|^42$|^43$|^44$|^45$|^46$|^47$|^48$|^49$|^50$|^51$|^52$|^53$|^54$|^55$|^56$|^57$|^58$|^59$|^60$|^61$|^62$|^63$|^64$|^65$|^66$|^67$|^68$|^69$|^70$|^71$|^72$|^73$|^74$|^75$|^76$|^77$|^78$|^79$|^80$|^81$|^82$|^83$|^84$|^85$|^86$|^87$|^88$|^89$|^90$|^91$|^92$|^93$' --workers 10

$w/bin/db_ctl.sh $REPO stop


