#!/bin/bash

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

# add warps
python processing/stampede/coadds/fixup/warps.py $REPO data/coadd_fixup_2/exclude_visits.csv allSky/fixup_2 --collections DEEP/allSky/fixup/coadd/warps

# warp counts
python bin/warp_counts.py $REPO --collections DEEP/allSky/fixup_2/coadd/warps > ./data/coadd_fixup_2/warp_counts.csv

group_0=$(python bin/select_patches.py ./data/coadd_fixup_2/warp_counts.csv)
# group_1=$(python bin/select_patches.py ./data/coadd_fixup_2/warp_counts.csv --min 150)
{
    python bin/warps.py "${REPO}" "allSky/fixup_2/0" --where "skymap='discrete' and patch in (${group_0})" --collections "DEEP/allSky/fixup_2/coadd/warps"
    python bin/collection.py "${REPO}" coadd allSky/fixup_2/0
} &
# {
#     python bin/warps.py "${REPO}" "allSky/fixup/1" --where "skymap='discrete' and patch in (${group_1})" --collections "DEEP/allSky/fixup/coadd/warps"
#     python bin/collection.py "${REPO}" coadd allSky/fixup/1
# } &
wait
# # shard warps
# python bin/split_warp_inputs.py ./data/coadd_fixup_2/warp_counts.csv ./data/coadd_fixup_2/warp_subsets --max-warps 100

# # add warps/make collections
# for f in ./data/coadd_fixup_2/warp_subsets/*.csv; do
#     i=$(echo $(basename ${f}) | tr -d '.csv')
#     patches=$(python bin/select_patches.py ${f})
#     {
#         python bin/warps.py "${REPO}" "allSky/fixup/${i}" --where "skymap='discrete' and patch in (${patches})" --collections "DEEP/allSky/fixup/coadd/warps"
#         python bin/collection.py "${REPO}" coadd allSky/fixup/${i}
#     } &
# done
# wait

cleanup