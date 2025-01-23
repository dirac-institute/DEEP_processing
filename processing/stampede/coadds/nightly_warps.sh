#!/usr/bin/env bash
#SBATCH --partition=skx
#SBATCH --time=24:00:00
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

$w/bin/db_ctl.sh $REPO start

nights=$(echo ${w}/repo/DEEP/[0-9]*[0-9] | tr ' ' '\n' | awk -F"/" '{print $NF}')
echo "${nights}" | xargs -I % python bin/warps.py "${REPO}" % --collections DEEP/%/drp --where "instrument='DECam' and detector not in (31, 61)" > $w/processing/stampede/coadds/nightly_warps.log

cleanup
