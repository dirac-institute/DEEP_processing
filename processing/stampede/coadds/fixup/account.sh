#!/bin/bash
set -eux

cd "${DEEP_PROJECT_DIR}/data/coadd_fixup"

{
    coadd_collections=$(butler query-collections "${REPO}" "DEEP/allSky/*/coadd" | grep "CHAINED" | grep -v "fixup" | awk '{print $1}' | tr '\n' ' ')
    butler collection-chain "${REPO}" DEEP/allSky/coadd DEEP/allSky/coadd/warps skymaps ${coadd_collections}
} &

{
    grep -E ".*failed. Exception [a-zA-Z]+:" "${DEEP_PROJECT_DIR}"/submit/DEEP/allSky/*/coadd/DEEP-template/assembleCoadd/*/logs/assembleCoadd/*/*/*/*.stderr > failures.dat
    cat failures.dat | sed -nE "s/.*failed. Exception (.*)/\1/p" | sort | uniq > failure_reasons.dat
} &

{ 
    grep -E "Found 0 deepCoadd_directWarp|Found 0 deepCoadd_psfMatchedWarp" "${DEEP_PROJECT_DIR}"/submit/DEEP/allSky/*/coadd/DEEP-template/assembleCoadd/*/logs/assembleCoadd/*/*/*/*.stderr > no_coverage.dat
    cat no_coverage.dat | sed -nE "s/.*band: '([a-zA-Z]+)',.*patch: ([0-9]+).*/\2,\1/p" > no_coverage.csv
} &

wait

function inner() {
    band=$1
    butler query-dimension-records "${REPO}" patch --datasets deepCoadd_directWarp --where "instrument='DECam' and skymap='discrete' and band='${band}'" --collections "DEEP/allSky/coadd/warps" > "patches_${band}.dat"
    cat "patches_${band}.dat" | awk '{print $3}' | grep -E "[0-9]+" | sort -n | uniq > "patches_${band}_uniq.dat"

    butler query-dimension-records "${REPO}" patch --datasets deepCoadd --where "instrument='DECam' and skymap='discrete' and band='${band}'" --collections "DEEP/allSky/coadd" > "patches_${band}_coadd.dat"
    cat "patches_${band}_coadd.dat" | awk '{print $3}' | grep -E "[0-9]+" | sort -n | uniq > "patches_${band}_coadd_uniq.dat"

    diff "patches_${band}_uniq.dat" "patches_${band}_coadd_uniq.dat" | grep "<" | awk '{print $2}' > "patches_${band}_missing.dat"
    
    cat exclude_visits.csv | grep "${band}," | awk -F"," '{print $1}' | sort -n | uniq > "patches_${band}_fixup.dat"

    cat no_coverage.csv | grep ",${band}" | awk -F"," '{print $1}' | sort -n | uniq > "patches_${band}_no_data.dat"

    diff "patches_${band}_missing.dat" "patches_${band}_no_data.dat"  | grep "<" | awk '{print $2}' > "patches_${band}_failed.dat"

    diff "patches_${band}_failed.dat" "patches_${band}_fixup.dat" | grep "<" | awk '{print $2}' > "patches_${band}_not_fixed.dat"

    cat "patches_${band}_not_fixed.dat" | xargs -I % grep -E "_%_" failures.dat | sed -nE "s/.*patch: ([0-9]+).*/\1/p" > "patches_${band}_accounted.dat"
    echo "${band}" && diff "patches_${band}_not_fixed.dat" "patches_${band}_accounted.dat"
}

bands="i r VR"
for band in ${bands}; do
    inner "${band}" &
done
wait
