#!/bin/bash
#SBATCH --partition=skx
#SBATCH --time=2:00:00
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

for f in ./data/warp_subsets/*.csv; do
    i=$(echo $(basename ${f}) | tr -d '.csv')
    patches=$(python bin/select_patches.py ${f})
    python bin/warps.py "${REPO}" "allSky/${i}" --where "skymap='discrete' and patch in (${patches})" --collections "DEEP/*/drp" &
done

$w/bin/db_ctl.sh $REPO stop

disown
