#!/usr/bin/env bash

w=$DEEP_PROJECT_DIR
cd $w
source $w/bin/setup.sh

mkdir -p data/coadd_fixup_2

grep "Exception RuntimeError: Polygon is not convex" submit/DEEP/allSky/fixup/*/coadd/DEEP-template/assembleCoadd/*/logs/assembleCoadd/*/*/*/*.stderr > data/coadd_fixup_2/polygon_failures.dat
cat data/coadd_fixup_2/polygon_failures.dat | awk -F":" '{print $1}' | xargs -P 40 -I % python bin/fixup_coadd_polygon.py $REPO --input % | grep -E "[0-9]+,[a-zA-Z]+,[0-9]+" | sort -n | uniq > data/coadd_fixup_2/polygon_exclude_visits.csv

grep -E "Exception AttributeError" submit/DEEP/allSky/fixup/*/coadd/DEEP-template/assembleCoadd/*/logs/assembleCoadd/*/*/*/*.stderr > data/coadd_fixup_2/mismatched_failures.dat
python bin/fixup_coadd_mismatch.py --input $(cat data/coadd_fixup_2/mismatched_failures.dat | awk -F":" '{print $1}') | grep -E "[0-9]+,[a-zA-Z]+,[0-9]+" | sort -n | uniq > data/coadd_fixup_2/mismatched_exclude_visits.csv

cat data/coadd_fixup_2/polygon_exclude_visits.csv > data/coadd_fixup_2/exclude_visits.csv.bak
cat data/coadd_fixup_2/mismatched_exclude_visits.csv >> data/coadd_fixup_2/exclude_visits.csv.bak 
echo "patch,band,visit" > data/coadd_fixup_2/exclude_visits.csv
cat data/coadd_fixup_2/exclude_visits.csv.bak | sort | uniq >> data/coadd_fixup_2/exclude_visits.csv
rm -f data/coadd_fixup_2/exclude_visits.csv.bak