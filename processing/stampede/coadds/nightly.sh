#!/usr/bin/env bash
#SBATCH --partition=skx
#SBATCH --time=4:00:00
#SBATCH --nodes=1

w=$DEEP_PROJECT_DIR
cd $w
source $w/bin/setup.sh

export PROC_LSST_SITE="stampede" #${PROC_LSST_SITE:-"stampede"}
export PROC_LSST_QUEUE="multi" # ${PROC_LSST_QUEUE:-"multi"}
export PROC_LSST_MULTI_QUEUES="local,skx" # ${PROC_LSST_MULTI_QUEUES:-"local,skx"}
export PROC_LSST_NODES_PER_BLOCK="1" #${PROC_LSST_NODES_PER_BLOCK:-1}
export PROC_LSST_CORES_PER_NODE="12" # ${PROC_LSST_CORES_PER_NODE:-48}
export PROC_LSST_MAX_BLOCKS="9" # ${PROC_LSST_MAX_BLOCKS:-1}
export PROC_LSST_WALLTIME="2:00:00"
export J=3 # cores per worker for local
env | grep PROC_LSST

function cleanup() {
    $w/bin/db_ctl.sh $w/repo stop
}

trap cleanup SIGINT
trap cleanup SIGTERM
trap cleanup SIGEXIT

$w/bin/db_ctl.sh $REPO start

nights=$(echo "$@" | tr ' ' '\n')
echo "${nights}" | xargs -I % -P 4 python bin/warps.py "${REPO}" % --collections DEEP/%/drp --where "instrument='DECam' and detector not in (31, 61)"
echo "${nights}" | xargs -I % -P 4 python bin/collection.py "${REPO}" coadd %
selection=$(echo "$nights" | python -c "import sys; print('(' + '|'.join(sum(map(lambda x : x.split(), sys.stdin.readlines()), [])) + ')')")

python bin/pipeline.py "${REPO}" coadd "${selection}" --workers 4

cleanup
