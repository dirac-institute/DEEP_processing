# Processing

## Biases
Make survey biases:
```
$ sbatch processing/stampede/bias.sh
```

Missing bias:
```
$ bash processing/stampede/missing_bias.sh
```

## Flats

Make survey flats:
```
$ sbatch processing/stampede/flat.sh
```

Missing flat:
```
$ bash processing/stampede/missing_flat.sh
```

## DRP

```
$ sbatch processing/stampede/drp.sh
```

## Warps

```
$ ./bin/db_ctl.sh ./repo start
$ python bin/warps.py ./repo allSky --collections "DEEP/*/drp"
INFO:__main__:associatating 997600 of deepCoadd_psfMatchedWarp into DEEP/allSky/coadd/warps
INFO:__main__:associatating 997600 of deepCoadd_directWarp into DEEP/allSky/coadd/warps
$ ./bin/db_ctl.sh ./repo stop
```

## All Sky Coadd

Group warps by input number.
```
$ python ./bin/warp_counts.py $REPO --collections DEEP/allSky/coadd/warps > ./data/warp_counts_allSky.csv
$ python bin/split_warp_inputs.py ./data/warp_counts_allSky.csv ./data/warp_subsets
```

Make warp collections:
```
$ sbatch processing/stampede/coadds/warp_collections.sh
```

Excecute coadds on groups:
- (6 GB/Core; 0 < n <= 50): subsets 0-5 
```
$ sbatch processing/stampede/coadds/small.sh
```
- (12 GB/Core; 50 < n <= 150): subsets 6-16
- (16 GB/core; 150 < n <= 300): subsets 17-37
- (20 GB/core; 300 < n <= 450): subsets 38-57


RuntimeError: Polygon is not convex
```bash
$ tail -n 1 submit/DEEP/allSky/*/coadd/DEEP-template/assembleCoadd/*/logs/assembleCoadd/*/*/*/*.stderr | grep -B 1 "One or more tasks fail" | grep "==>" | awk '{print $2}' | xargs -I % grep "RuntimeError: Polygon" % > polygon.dat &
$ patches=$( cat polygon.dat | sed -nE "s/.*patch: ([0-9]+).*/\1/p" | sort -n | paste -sd, )
$ python bin/warps.py $REPO allSky/fixup --collections DEEP/allSky/coadd/warps --where "instrument='DECam' and skymap='discrete' and patch in (${patches}) and detector not in (31)"
$ python bin/collection.py $REPO coadd allSky --coadd-subset fixup
```

patches: 38333 38683 38684 44917 44918 45268 72282 72283 72284 72632 72632 72633 72634 74378 74379 74728 74729 74738 77539 77889

38333 {1, 2, 5, 6, 44, 50}
38683 {50, 44, 38}
38684 {37, 38, 43, 44, 49, 50}
44917 {36, 37, 38, 44, 29, 30, 31}
44918 {36, 37, 38, 42, 44, 29, 30, 31}
45268 {37, 38, 22, 23, 24, 28, 29, 30, 31}
72282 {38, 13, 14, 19, 20, 26, 27, 31}
72283 {38, 13, 19, 24, 25, 26, 31}
72284 {37, 38, 13, 19, 23, 24, 25, 30, 31}
72632 {8, 9, 13, 14, 31}
72632 {8, 9, 13, 14, 31}
72633 {8, 13, 18, 24, 31}
72634 {13, 17, 18, 23, 24, 30, 31}
74378 {44, 38, 31}
74379 {37, 38, 44, 30, 31}
74728 {24, 31}
74729 {24, 30, 31}
74738 {36, 37, 38, 43, 44, 25, 29, 30, 31}
77539 {38, 13, 14, 19, 20, 24, 25, 26, 31}
77889 {8, 13, 14, 18, 24, 31}

```
$ pipetask qgraph -b $REPO -p ./pipelines/DEEP-template.yaml#assembleCoadd -i DEEP/allSky/coadd/warps -o DEEP/allSky/fixup -d "instrument='DECam' and skymap='discrete' and patch in (${patches}) and detector not in (31)" --save-qgraph fixup.qgraph
```

My guess is inclusion of detector 31 seems to be the culprit

There is at least empty direct/psfMatched warp where the complementary type is non-empty
AttributeError: 'NoneType' object has no attribute 'ccds'
```bash
$ tail -n 1 submit/DEEP/allSky/*/coadd/DEEP-template/assembleCoadd/*/logs/assembleCoadd/*/*/*/*.stderr | grep -B 1 "One or more tasks fail" | grep "==>" | awk '{print $2}' | xargs -I % grep "AttributeError" % > mismatch.dat
$ cat mismatch.dat | sed -nE "s/.*patch: ([0-9]+).*/\1/p" | sort -n | tr '\n' ' '
```

mismatch: 35437 35437 38334 42809 43159 45257 45258 45612 47701 47702 50156 60470 77531 95834 95834 103648

35437 {1, 3}
35437 {1, 3}
38334 {1, 2, 4, 5, 43, 44, 49, 50, 55}
42809 {38, 31}
43159 {38, 45, 46, 51, 52, 24, 56, 31}
45257 {1, 2, 4, 5, 9, 10, 60}
45258 {1, 4, 5, 8, 9, 44, 50}
45612 {35, 36, 41, 42, 47, 48}
47701 {17, 18, 12, 7}
47702 {7, 11, 12, 17, 18}
50156 {25, 26, 19, 20}
60470 {20, 21, 14, 15}
77531 {24, 18, 31}
95834 {32, 47, 48, 53, 54, 58}
95834 {32, 47, 48, 53, 54, 58}
103648 {37, 38, 8, 9, 10, 13, 15, 16, 21, 22, 24, 30, 31}



```
$ echo repo/DEEP/allSky/{94,95,96,97,98,99,100,101}/coadd/DEEP-template/assembleCoadd/*/deepCoadd/*/*/{i,r}/*.fits | tr ' ' '\n' | grep -v '*' | awk -F"/" '{print $4, $10, $11, $12}' | sort -k 1 -n > complete.dat
$ echo submit/DEEP/allSky/{94,95,96,97,98,99,100,101}/coadd/DEEP-template/assembleCoadd/*/logs/assembleCoadd/*/*/{i,r}/*.stderr | tr ' ' '\n' | grep -v "*" | awk -F"/" '{print $4, $11, $12, $13}' | sort -n -k 1 > inprogress.dat
$ diff inprogress.dat complete.dat
```

```
$ ./bin/db_ctl.sh ./repo start
$ final=$(ls submit/DEEP/allSky/{94,95,96,97,98,99,100,101}/coadd/DEEP-template/assembleCoadd/*/final_job.bash)
$ for f in $final; do echo $f; $f $(find $(dirname $f) -name "*Z.qgraph") $REPO; done
$ ./bin/db_ctl.sh ./repo stop
```

```
$ runs=$(butler query-collections $REPO --collection-type RUN | grep RUN | awk '{print $1}')
$ echo "$runs" | xargs -P 40 -I % mkdir -p ./processing/stampede/statistics/storage/%
$ echo "$runs" | xargs -P 40 -I % python bin/size.py $REPO "*" --agg --collections % --output ./processing/stampede/statistics/storage/%/size.csv & disown
```

```
$ cat ./processing/stampede/statistics/storage_summary.csv | grep -E "raw,|*postISRCCD*|*icExp*|deepCoadd_.*Warp|overscanRaw|cpBiasIsrExp|cpFlatIsrExp" | awk -F"," '{print $2}' | paste -sd+ | bc
841184581689784
$ cat ./processing/stampede/statistics/storage_summary.csv | awk -F"," '{print $2}' | paste -sd+ | bc
932837021437153
```

About 100TB of data excluding what we don't want to export

Let me start an rsync back to Epyc of the repo...

```
$ rsync -avL --exclude {"raw","*postISRCCD*","*icExp*","deepCoadd*Warp","overscanRaw","cpBiasIsrExp","cpFlatIsrExp"} ./repo/DEEP/20190401/drp/DEEP epyc:/epyc/data4/stampede_repo/.
```

```
$ python bin/transfer.py ./repo/ epyc /epyc/data4/stampede_repo/ --exclude "raw" --exclude "*postISRCCD*" --exclude "*icExp*" --exclude "deepCoadd*Warp" --exclude "overscanRaw" --exclude "cpBiasIsrExp" --exclude "cpFlatIsrExp"
```

```
$ echo "${runs}" | xargs -P 40 -I % python bin/transfer.py ./repo/% epyc /epyc/data4/stampede_repo/% --exclude "raw" --exclude "*postISRCCD*" --exclude "*icExp*" --exclude "deepCoadd*Warp" --exclude "overscanRaw" --exclude "cpBiasIsrExp" --exclude "cpFlatIsrExp" >> transfer.log 2>&1 & disown
```
3440441

Polygon solution

```
refs = list(set(list(butler.registry.queryDatasets("deepCoadd_directWarp", where=f"instrument='DECam' and skymap='discrete' and patch={patch} and band={band} and detector=31", collections="DEEP/allSky/coadd/warps"))))
refs_c = list(set(list(butler.registry.queryDatasets("deepCoadd_directWarp", where=f"instrument='DECam' and skymap='discrete' and patch={patch} and band={band} and detector!=31", collections="DEEP/allSky/coadd/warps"))))

fixed = list(set(refs_c).difference(set(refs)))

for ref in fixed:
    patch = ref.dataId['patch']; visit = ref.dataId['visit'];
    assert(31 not in list(set(list(map(lambda x : x.id, butler.registry.queryDimensionRecords("detector", where=f"instrument='DECam' and skymap='discrete' and patch={patch} and visit={visit}"))))))

butler.registry.associate(fixed, "DEEP/allSky/fixup/coadd/warps")
```


```
included = re.compile("INFO.*Weight of (.*) \{.*visit: (\d+),.*band: '(\w+)',.*\}.*")
excluded = re.compile("WARNING.*(deepCoadd_.*Warp)_.*with data ID \{.*visit: (\d+),.*band: '(\w+)',.*\}.*")

with open("submit/DEEP/allSky/0/coadd/DEEP-template/assembleCoadd/20241219T220259Z/logs/assembleCoadd/10/95834/r/91491fc7-314b-44c3-a870-6b9a54c53aef_assembleCoadd_10_95834_r_.stderr", "r") as f:
```

cat polygon2.dat | sed -nE "s/.*patch: ([0-9]+).*band: '(\w+)'.*/\1 \2/p" | sort -n -k 1
38333 VR
38683 VR
38684 VR
44917 VR
44918 VR
45268 VR
72282 VR
72283 VR
72284 VR
72632 VR
72632 VR
72633 VR
72634 VR
74378 VR
74379 VR
74389 VR
74728 VR
74729 VR
74738 VR
74739 VR
74740 VR
77539 VR
77540 VR
77889 VR
77890 VR

```bash
$ grep -E "Exception AttributeError" submit/DEEP/allSky/*/coadd/DEEP-template/assembleCoadd/*/logs/assembleCoadd/*/*/*/*.stderr > mismatched2.log
$ cat mismatched2.log | awk -F":" '{print $1}' | xargs -I % python bin/fixup_coadd_mismatch.py $REPO DEEP/allSky/fixup/coadd/warps --input %
```

```bash
$ grep "Exception RuntimeError: Polygon is not convex" submit/DEEP/allSky/*/coadd/DEEP-template/assembleCoadd/*/logs/assembleCoadd/*/*/*/*.stderr > polygon2.dat
$ cat polygon2.dat | sed -nE "s/.*patch: ([0-9]+).*band: '(\w+)'.*/\1 \2/p" | sort -n -k 1 | awk '{print $1}' | xargs -I % python bin/fixup_coadd_polygon.py $REPO DEEP/allSky/fixup/coadd/warps --patch % --band VR
```

```bash
$ python bin/fixup_coadd_mismatch.py $REPO DEEP/allSky/fixup/coadd/warps --input $(cat mismatched2.log | awk -F":" '{print $1}') > mismatched_patches.csv
```

```bash
$ pipetask qgraph -b $REPO -o DEEP/allSky/fixup/coadd -p ./pipelines/DEEP-template.yaml -d "instrument='DECam' and skymap='discrete' and (patch=35437 and band='r')" --save-qgraph fixup_35437.qgraph
$ PROC_LSST_SITE="stampede" PROC_LSST_QUEUE="multi" PROC_LSST_MULTI_QUEUES="local,skx" PROC_LSST_NODES_PER_BLOCK="1" PROC_LSST_CORES_PER_NODE="24" PROC_LSST_MAX_BLOCKS="4" PROC_LSST_WALLTIME="8:00:00" J="24" bps submit ${PROC_LSST_DIR}/pipelines/submit.yaml -b $REPO -o DEEP/allSky/fixup/coadd --qgraph fixup_35437.qgraph
```

```bash
$ PROC_LSST_SITE="stampede" PROC_LSST_QUEUE="multi" PROC_LSST_MULTI_QUEUES="local,skx" PROC_LSST_NODES_PER_BLOCK="1" PROC_LSST_CORES_PER_NODE="24" PROC_LSST_MAX_BLOCKS="4" PROC_LSST_WALLTIME="8:00:00" J="24" python bin/pipeline.py $REPO coadd allSky --coadd-subset fixup --steps assembleCoadd --where "instrument='DECam' and skymap='discrete' and (patch=35437 and band='r')"
```

```bash
$ f="data/coadd_fixup/polygon_fixup.csv" echo "patch,band" > ${f}; cat polygon2.dat | sed -nE "s/.*patch: ([0-9]+).*band: '(\w+)'.*/\1,\2/p" >> ${f}
```

```
$ python bin/collection.py $REPO coadd allSky --coadd-subset fixup
$ PROC_LSST_SITE="stampede" PROC_LSST_QUEUE="multi" PROC_LSST_MULTI_QUEUES="local,skx" PROC_LSST_NODES_PER_BLOCK="1" PROC_LSST_CORES_PER_NODE="24" PROC_LSST_MAX_BLOCKS="4" PROC_LSST_WALLTIME="8:00:00" J="24" python bin/pipeline.py $REPO coadd allSky --coadd-subset fixup --steps assembleCoadd --where "instrument='DECam' and skymap='discrete' and ((patch=35437 and band='r') or (patch=72633 and band='VR'))"
```

```bash
$ python bin/warp_counts.py $REPO --collections DEEP/allSky/fixup/coadd/warps > data/coadd_fixup/warp_counts.csv
$ python bin/split_warp_inputs.py ./data/coadd_fixup/warp_counts.csv ./data/coadd_fixup/groups --group
```

Verify that allSky/coadd/* has a deepCoadd for every patch covered by the survey

found 12400 coadd logs
there are 12288 of assembleCoadd_metadata

```
$ cat data/coadd_fixup/exclude_visits.csv | awk -F"," '{print $1}' | grep -E "[0-9]+" | sort -n | uniq | wc -l
65
```

Plan how to do diff_drp...put it in night.py and handle coadd types to pass to collection

$ butler query-dimension-records $REPO patch --datasets calexp --where "instrument='DECam' and skymap='discrete'" --collections "DEEP/*/drp"

7195 patches_VR_uniq.dat
4535 patches_r_uniq.dat
297 patches_i_uniq.dat

$ coadd_collections=$(butler query-collections $REPO "DEEP/allSky/*/coadd" | grep "CHAINED" | grep -v "fixup" | awk '{print $1}' | tr '\n' ' ')
$ butler collection-chain $REPO DEEP/allSky/coadd DEEP/allSky/coadd/warps skymaps ${coadd_collections}

$ butler query-dimension-records $REPO patch --datasets deepCoadd --where "instrument='DECam' and skymap='discrete' and band='i'" --collections "DEEP/allSky/coadd" > patches_i_coadd.dat
 
```
$ wc -l patches_i_coadd_uniq.dat
284 patches_i_coadd_uniq.dat

$ wc -l patches_r_coadd_uniq.dat
4300 patches_r_coadd_uniq.dat

$ wc -l patches_VR_coadd_uniq.dat
6677 patches_VR_coadd_uniq.dat
```

$ diff patches_i_uniq.dat patches_i_coadd_uniq.dat | grep "<" | awk '{print $2}' > patches_i_missing.dat
14366
14369
15772
16113
16122
16472
59092
59788
60148
61897
62246
73361
73710


$ cat data/coadd_fixup/exclude_visits.csv | grep "VR," | awk -F"," '{print $1}' | sort -n | uniq > patches_VR_fixup.dat
$ cat data/coadd_fixup/exclude_visits.csv | grep "r," | awk -F"," '{print $1}' | sort -n | uniq > patches_r_fixup.dat

$ grep -E "Found 0 deepCoadd_directWarp|Found 0 deepCoadd_psfMatchedWarp" submit/DEEP/allSky/*/coadd/DEEP-template/assembleCoadd/*/logs/assembleCoadd/*/*/*/*.stderr > data/coadd_fixup/no_coverage.dat

$ cat data/coadd_fixup/no_coverage.dat | sed -nE "s/.*band: '([a-zA-Z]+)',.*patch: ([0-9]+).*/\2,\1/p" > data/coadd_fixup/no_coverage.csv
$ cat data/coadd_fixup/no_coverage.csv | grep ",r" | awk -F"," '{print $1}' | sort -n | uniq
$ cat data/coadd_fixup/no_coverage.csv | grep ",r" | awk -F"," '{print $1}' | sort -n | uniq > patches_r_no_data.dat
$ cat data/coadd_fixup/no_coverage.csv | grep ",i" | awk -F"," '{print $1}' | sort -n | uniq > patches_i_no_data.dat
$ cat data/coadd_fixup/no_coverage.csv | grep ",VR" | awk -F"," '{print $1}' | sort -n | uniq > patches_VR_no_data.dat

$ diff patches_i_missing.dat patches_i_no_data.dat  | grep "<" | awk '{print $2}' > patches_i_failed.dat
$ diff patches_i_failed.dat patches_i_fixup.dat

$ grep -E ".*failed. Exception [a-zA-Z]+:" submit/DEEP/allSky/*/coadd/DEEP-template/assembleCoadd/*/logs/assembleCoadd/*/*/*/*.stderr > data/coadd_fixup/failures.dat
$ cat data/coadd_fixup/failures.dat | sed -nE "s/.*failed. Exception (.*)/\1/p" | sort | uniq > data/coadd_fixup/failure_reasons.dat

AttributeError: 'NoneType' object has no attribute 'ccds'
MemoryError: Unable to allocate 13.7 MiB for an array with shape (2, 900000) and data type float64
MemoryError: Unable to allocate 154. MiB for an array with shape (4500, 4500) and data type float64
MemoryError: Unable to allocate 3.16 MiB for an array with shape (414187,) and data type float64
MemoryError: Unable to allocate 6.00 MiB for an array with shape (786432,) and data type int64
MemoryError: Unable to allocate 77.2 MiB for an array with shape (4500, 4500) and data type int32
RuntimeError: Polygon is not convex.
ValueError: Failure from formatter 'lsst.obs.base.formatters.fitsExposure.FitsExposureFormatter' for dataset 1129add3-02b1-426c-ac9d-52ba43d71a9b (deepCoadd_directWarp from file:///scratch/10000/stetzler/DEEP_processing/repo/DEEP/20210910/drp/DEEP-DRP/step3a/20241217T203526Z/deepCoadd_directWarp/5/3286/20210910/VR/VR_DECam_c0007_6300.0_2600.0/1032298/deepCoadd_directWarp_DECam_5_3286_VR_VR_DECam_c0007_6300_0_2600_0_1032298_discrete_DEEP_20210910_drp_DEEP-DRP_step3a_20241217T203526Z.fits): std::bad_alloc
ValueError: Failure from formatter 'lsst.obs.base.formatters.fitsExposure.FitsExposureFormatter' for dataset 7d23e474-94c4-4c70-887e-df49aa34f7b3 (deepCoadd_directWarp from file:///scratch/10000/stetzler/DEEP_processing/repo/DEEP/20220526/drp/DEEP-DRP/step3a/20241215T221208Z/deepCoadd_directWarp/4/13655/20220526/VR/VR_DECam_c0007_6300.0_2600.0/1101027/deepCoadd_directWarp_DECam_4_13655_VR_VR_DECam_c0007_6300_0_2600_0_1101027_discrete_DEEP_20220526_drp_DEEP-DRP_step3a_20241215T221208Z.fits): std::bad_alloc
ValueError: Failure from formatter 'lsst.obs.base.formatters.fitsExposure.FitsExposureFormatter' for dataset a8a9772d-4c3b-4345-8a63-d326899c3383 (deepCoadd_psfMatchedWarp from file:///scratch/10000/stetzler/DEEP_processing/repo/DEEP/20220827/drp/DEEP-DRP/step3a/20241215T180911Z/deepCoadd_psfMatchedWarp/6/76847/20220827/VR/VR_DECam_c0007_6300.0_2600.0/1126368/deepCoadd_psfMatchedWarp_DECam_6_76847_VR_VR_DECam_c0007_6300_0_2600_0_1126368_discrete_DEEP_20220827_drp_DEEP-DRP_step3a_20241215T180911Z.fits): std::bad_alloc


Get runs for all of these and attempt retry script
```bash
$ sed -nE "s/.*submit\/(.*)\/logs.*/\1/p" data/coadd_fixup/failures.dat | xargs -I % python bin/retries.py $REPO %
$ ./bin/db_ctl.sh ./repo stop && sbatch processing/stampede/coadds/all.sh
```


$ diff patches_i_failed.dat patches_i_fixup.dat | grep "<" | awk '{print $2}' > patches_i_not_fixed.dat
$ diff patches_r_failed.dat patches_r_fixup.dat | grep "<" | awk '{print $2}' > patches_r_not_fixed.dat
$ diff patches_VR_failed.dat patches_VR_fixup.dat | grep "<" | awk '{print $2}' > patches_VR_not_fixed.dat

$ wc -l patches_i_not_fixed.dat; cat patches_i_not_fixed.dat | xargs -I % grep -E "_%_" data/coadd_fixup/failures.dat | wc -l
1 patches_i_not_fixed.dat
1
$ wc -l patches_r_not_fixed.dat; cat patches_r_not_fixed.dat | xargs -I % grep -E "_%_" data/coadd_fixup/failures.dat | wc -l
1 patches_r_not_fixed.dat
0
$ wc -l patches_VR_not_fixed.dat; cat patches_VR_not_fixed.dat | xargs -I % grep -E "_%_" data/coadd_fixup/failures.dat | wc -l
455 patches_VR_not_fixed.dat
17

$ cat patches_VR_not_fixed.dat | xargs -I % grep -E "_%_" data/coadd_fixup/failures.dat | sed -nE "s/.*patch: ([0-9]+).*/\1/p" > patches_VR_accounted.dat
$ cat patches_r_not_fixed.dat | xargs -I % grep -E "_%_" data/coadd_fixup/failures.dat | sed -nE "s/.*patch: ([0-9]+).*/\1/p" > patches_r_accounted.dat
$ cat patches_i_not_fixed.dat | xargs -I % grep -E "_%_" data/coadd_fixup/failures.dat | sed -nE "s/.*patch: ([0-9]+).*/\1/p" > patches_i_accounted.dat

$ diff patches_VR_not_fixed.dat patches_VR_accounted.dat
$ diff patches_r_not_fixed.dat patches_r_accounted.dat
$ diff patches_i_not_fixed.dat patches_i_accounted.dat

Everything is accounted for.

Should have fixed up the mismatched and then the polygon. Because some of the mismatched are encountering the polygon error...oops

grep -E "not excluding|not including" /scratch/10000/stetzler/DEEP_processing/processing/stampede/coadds/fixup/exclude_visits_2.log | sed -nE "s/.*patch=([0-9]+).*/\1/p" | sort -n > patches_not_excluded.dat

diff patches_VR_not_fixed.dat patches_not_excluded.dat | grep "<"
< 74378
< 74379
< 74728
< 74729

Union of:
- existing deepCoadd
- no_data
- not_excluded
should qual
- all patches

$ cat patches_i_coadd_uniq.dat patches_not_excluded.dat patches_i_no_data.dat | sort -n | uniq > patches_i_total.dat
$ diff patches_i_total.dat patches_i_uniq.dat | grep ">"
$ cat patches_r_coadd_uniq.dat patches_not_excluded.dat patches_r_no_data.dat | sort -n | uniq > patches_r_total.dat
$ diff patches_r_total.dat patches_r_uniq.dat | grep ">"
> 82946
$ cat patches_VR_coadd_uniq.dat patches_not_excluded.dat patches_VR_no_data.dat | sort -n | uniq > patches_VR_total.dat
$ diff patches_VR_total.dat patches_VR_uniq.dat | grep ">"

So there is only one patch in r-band that doesn't have a deepCoadd

```
$ cat ./processing/stampede/statistics/storage_summary.csv | grep -E "raw,|*postISRCCD*|*icExp*|deepCoadd_.*Warp|overscanRaw|cpBiasIsrExp|cpFlatIsrExp|deepDiff_templateExp|deepDiff_matchedExp|deepDiff_differenceTempExp" | awk -F"," '{print $2}' | paste -sd+ | bc
881704897241464
$ cat ./processing/stampede/statistics/storage_summary.csv | awk -F"," '{print $2}' | paste -sd+ | bc
974066870303773
```
84 TB


  Package                                        Version  Build                         Channel           Size
────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Install:
────────────────────────────────────────────────────────────────────────────────────────────────────────────────

  + _libgcc_mutex                                    0.1  conda_forge                   conda-forge     Cached
  + ld_impl_linux-64                                2.43  h712a8e2_2                    conda-forge      669kB
  + ca-certificates                           2024.12.14  hbcca054_0                    conda-forge      157kB
  + python_abi                                      3.11  5_cp311                       conda-forge        6kB
  + git-lfs                                        3.6.0  h647637d_0                    conda-forge        4MB
  + libboost-headers                              1.82.0  ha770c72_3                    conda-forge       14MB
  + mpi                                              1.0  openmpi                       conda-forge        4kB
  + libgomp                                       14.2.0  h77fa898_1                    conda-forge      461kB
  + _openmp_mutex                                    4.5  2_gnu                         conda-forge     Cached
  + libgcc                                        14.2.0  h77fa898_1                    conda-forge      849kB
  + libnl                                         3.11.0  hb9d3cd8_0                    conda-forge      741kB
  + reproc                                  14.2.5.post0  hb9d3cd8_0                    conda-forge       34kB
  + libntlm                                          1.8  hb9d3cd8_0                    conda-forge       33kB
  + oniguruma                                     6.9.10  hb9d3cd8_0                    conda-forge      249kB
  + libdeflate                                      1.23  h4ddbbb0_0                    conda-forge       72kB
  + libbrotlicommon                                1.1.0  hb9d3cd8_2                    conda-forge       69kB
  + aws-c-common                                  0.10.6  hb9d3cd8_0                    conda-forge      237kB
  + xorg-libxau                                   1.0.12  hb9d3cd8_0                    conda-forge       15kB
  + xorg-libxdmcp                                  1.1.5  hb9d3cd8_0                    conda-forge       20kB
  + pthread-stubs                                    0.4  hb9d3cd8_1002                 conda-forge        8kB
  + libcxxabi                                     16.0.6  h4bc722e_2                    conda-forge      153kB
  + libwebp-base                                   1.5.0  h851e524_0                    conda-forge      430kB
  + c-ares                                        1.34.4  hb9d3cd8_0                    conda-forge      206kB
  + libutf8proc                                    2.9.0  hb9d3cd8_1                    conda-forge       82kB
  + make                                           4.4.1  hb9d3cd8_2                    conda-forge      513kB
  + rhash                                          1.4.5  hb9d3cd8_0                    conda-forge      187kB
  + libuv                                         1.49.2  hb9d3cd8_0                    conda-forge      885kB
  + libgfortran5                                  14.2.0  hd5240d6_1                    conda-forge        1MB
  + openssl                                        3.4.0  h7b32b05_1                    conda-forge        3MB
  + libzlib                                        1.3.1  hb9d3cd8_2                    conda-forge       61kB
  + liblzma                                        5.6.3  hb9d3cd8_1                    conda-forge      111kB
  + libexpat                                       2.6.4  h5888daf_0                    conda-forge       73kB
  + libstdcxx                                     14.2.0  hc0a3c3a_1                    conda-forge        4MB
  + libgcc-ng                                     14.2.0  h69a702a_1                    conda-forge       54kB
  + libbrotlienc                                   1.1.0  hb9d3cd8_2                    conda-forge      282kB
  + libbrotlidec                                   1.1.0  hb9d3cd8_2                    conda-forge       33kB
  + aws-c-compression                              0.3.0  h4e1184b_5                    conda-forge       19kB
  + aws-c-sdkutils                                 0.2.1  h4e1184b_4                    conda-forge       56kB
  + aws-checksums                                  0.2.2  h4e1184b_4                    conda-forge       73kB
  + libxcb                                        1.17.0  h8a09558_0                    conda-forge      396kB
  + libcxx                                        16.0.6  he02047a_2                    conda-forge      620kB
  + libgfortran                                   14.2.0  h69a702a_1                    conda-forge       54kB
  + s2n                                           1.5.10  hb5b8611_0                    conda-forge      355kB
  + aws-c-cal                                      0.8.1  h1a47875_3                    conda-forge       48kB
  + libpng                                        1.6.45  h943b412_0                    conda-forge      289kB
  + zlib                                           1.3.1  hb9d3cd8_2                    conda-forge       92kB
  + libssh2                                       1.11.1  hf672d98_0                    conda-forge      304kB
  + libsqlite                                     3.47.2  hee588c1_0                    conda-forge      874kB
  + expat                                          2.6.4  h5888daf_0                    conda-forge      138kB
  + libgpg-error                                    1.51  hbd13f7d_1                    conda-forge      269kB
  + reproc-cpp                              14.2.5.post0  h5888daf_0                    conda-forge       26kB
  + libsanitizer                                  12.4.0  h46f95d5_1                    conda-forge        4MB
  + zlib-ng                                        2.2.3  h7955e40_0                    conda-forge      109kB
  + zfp                                            1.0.1  h5888daf_2                    conda-forge      279kB
  + svt-av1                                        2.3.0  h5888daf_0                    conda-forge        3MB
  + gflags                                         2.2.2  h5888daf_1005                 conda-forge      120kB
  + snappy                                         1.2.1  h8bd8927_1                    conda-forge       43kB
  + lz4-c                                         1.10.0  h5888daf_1                    conda-forge      167kB
  + sleef                                            3.7  h1b44611_2                    conda-forge        2MB
  + libabseil                                 20240722.0  cxx17_hbbce691_4              conda-forge        1MB
  + libstdcxx-ng                                  14.2.0  h4852527_1                    conda-forge       54kB
  + attr                                           2.5.1  h166bdaf_1                    conda-forge       71kB
  + lzo                                             2.10  hd590300_1001                 conda-forge      171kB
  + rav1e                                          0.6.6  he8a937b_2                    conda-forge       15MB
  + libapriconv                                    1.2.2  hd590300_6                    conda-forge      592kB
  + dav1d                                          1.2.1  hd590300_0                    conda-forge      760kB
  + jxrlib                                           1.1  hd590300_3                    conda-forge      239kB
  + libjpeg-turbo                                  3.0.0  hd590300_1                    conda-forge      619kB
  + libev                                           4.33  hd590300_2                    conda-forge     Cached
  + libevent                                      2.1.12  hf998b51_1                    conda-forge      427kB
  + libiconv                                        1.17  hd590300_2                    conda-forge     Cached
  + libapr                                         1.7.0  hd590300_6                    conda-forge      383kB
  + giflib                                         5.2.2  hd590300_0                    conda-forge       77kB
  + pkg-config                                    0.29.2  h4bc722e_1009                 conda-forge      115kB
  + jq                                             1.7.1  hd590300_0                    conda-forge      319kB
  + yaml                                           0.2.5  h7f98852_2                    conda-forge       89kB
  + libsodium                                     1.0.20  h4ab18f5_0                    conda-forge      206kB
  + keyutils                                       1.6.1  h166bdaf_0                    conda-forge     Cached
  + tk                                            8.6.13  noxft_h4845f30_101            conda-forge     Cached
  + ncurses                                          6.5  he02047a_1                    conda-forge      889kB
  + libxcrypt                                     4.4.36  hd590300_1                    conda-forge     Cached
  + libffi                                         3.4.2  h7f98852_5                    conda-forge     Cached
  + bzip2                                          1.0.8  h4bc722e_7                    conda-forge      253kB
  + libuuid                                       2.38.1  h0b41bf4_0                    conda-forge     Cached
  + libnsl                                         2.0.1  hd590300_0                    conda-forge     Cached
  + brotli-bin                                     1.1.0  hb9d3cd8_2                    conda-forge       19kB
  + xorg-libx11                                   1.8.10  h4f16b4b_1                    conda-forge      838kB
  + libgfortran-ng                                14.2.0  h69a702a_1                    conda-forge       54kB
  + aws-c-io                                      0.15.3  h831e299_5                    conda-forge      158kB
  + freetype                                      2.12.1  h267a509_2                    conda-forge      635kB
  + libgcrypt-lib                                 1.11.0  hb9d3cd8_2                    conda-forge      586kB
  + libre2-11                                 2024.07.02  hbbce691_2                    conda-forge      210kB
  + libprotobuf                                   5.28.3  h6128344_1                    conda-forge        3MB
  + libzopfli                                      1.0.3  h9c3ff4c_0                    conda-forge      168kB
  + eigen                                          3.4.0  h00ab1b0_0                    conda-forge        1MB
  + gmp                                            6.3.0  hac33072_2                    conda-forge      460kB
  + x265                                             3.5  h924138e_3                    conda-forge        3MB
  + libde265                                      1.0.15  h00ab1b0_0                    conda-forge      412kB
  + libsolv                                       0.7.30  h3509ff9_0                    conda-forge      471kB
  + ninja                                         1.12.1  h297d8ca_0                    conda-forge        2MB
  + libhwy                                         1.1.0  h00ab1b0_0                    conda-forge        1MB
  + aom                                            3.9.1  hac33072_0                    conda-forge        3MB
  + libaec                                         1.1.3  h59595ed_0                    conda-forge       35kB
  + charls                                         2.4.2  h59595ed_0                    conda-forge      150kB
  + lerc                                           4.0.0  h27087fc_0                    conda-forge      282kB
  + gsoap                                        2.8.123  h8dc497d_0                    conda-forge        2MB
  + libllvm14                                     14.0.6  hcd5def8_4                    conda-forge       31MB
  + icu                                             75.1  he02047a_0                    conda-forge       12MB
  + xpa                                           2.1.20  h27087fc_1                    conda-forge      563kB
  + libcrc32c                                      1.1.2  h9c3ff4c_0                    conda-forge       20kB
  + glog                                           0.7.1  hbabe93e_0                    conda-forge      143kB
  + fmt                                           10.2.1  h00ab1b0_0                    conda-forge     Cached
  + zstd                                           1.5.6  ha6fb4c9_0                    conda-forge      555kB
  + minuit2_standalone                           6.22.06  h9c3ff4c_100                  conda-forge      512kB
  + yaml-cpp                                       0.8.0  h59595ed_0                    conda-forge     Cached
  + libcap                                          2.71  h39aace5_0                    conda-forge      102kB
  + libnghttp2                                    1.64.0  h161d5f1_0                    conda-forge      648kB
  + libthrift                                     0.21.0  h0e7cc3e_0                    conda-forge      426kB
  + doxygen                                       1.11.0  h9d7c8fd_0                    conda-forge       12MB
  + starlink-ast                                  9.2.10  hd590300_0                    conda-forge       17MB
  + libedit                                 3.1.20240808  pl5321h7949ede_0              conda-forge      135kB
  + readline                                         8.2  h8228510_1                    conda-forge     Cached
  + perl                                          5.32.1  7_hd590300_perl5              conda-forge       13MB
  + libaprutil                                     1.6.1  h40f5838_6                    conda-forge      218kB
  + munge                                         0.5.16  h63a00c3_0                    conda-forge      131kB
  + pcre2                                          10.43  hcad00b1_0                    conda-forge      951kB
  + brotli                                         1.1.0  hb9d3cd8_2                    conda-forge       19kB
  + fftw                                          3.3.10  nompi_hf1063bd_110            conda-forge        2MB
  + pgplot                                         5.2.2  hbeaba86_1009                 conda-forge      272kB
  + libopenblas                                   0.3.25  pthreads_h413a1c8_0           conda-forge        6MB
  + aws-c-event-stream                             0.5.0  h7959bf6_11                   conda-forge       54kB
  + aws-c-http                                     0.9.2  hefd7a92_4                    conda-forge      198kB
  + re2                                       2024.07.02  h9925aae_2                    conda-forge       27kB
  + mpfr                                           4.2.1  h90cbb55_3                    conda-forge      635kB
  + libjxl                                        0.11.1  hdb8da77_0                    conda-forge        2MB
  + libavif16                                      1.1.1  h1909e37_2                    conda-forge      116kB
  + voms                                        2.1.0rc3  h25bd2b9_0                    conda-forge      462kB
  + libxml2                                       2.13.5  h8d12d68_1                    conda-forge      691kB
  + spdlog                                        1.14.1  h597fd29_0                    conda-forge      197kB
  + c-blosc2                                      2.15.2  h3122c55_1                    conda-forge      342kB
  + blosc                                         1.21.6  he440d0b_1                    conda-forge       48kB
  + libtiff                                        4.7.0  hd9ff511_3                    conda-forge      428kB
  + minuit2                                      6.22.06  minuit2_standalone            conda-forge        6kB
  + libudev1                                       257.2  h9a4d06a_0                    conda-forge      144kB
  + libsystemd0                                    257.2  h3dc2cb9_0                    conda-forge      488kB
  + krb5                                          1.21.3  h659f571_0                    conda-forge        1MB
  + sqlite                                        3.47.2  h9eae976_0                    conda-forge      884kB
  + apr                                            1.7.0  hd590300_6                    conda-forge       49kB
  + libglib                                       2.80.2  hf974151_0                    conda-forge        4MB
  + htcondor-classads                             23.0.3  hc9a1274_0                    conda-forge       11MB
  + brunsli                                          0.1  h9c3ff4c_0                    conda-forge      205kB
  + ndarray                                        1.6.4  he5514bd_5                    conda-forge       46kB
  + openblas                                      0.3.25  pthreads_h7a3da1a_0           conda-forge        6MB
  + libblas                                        3.9.0  20_linux64_openblas           conda-forge       14kB
  + aws-c-auth                                     0.8.0  hb921021_15                   conda-forge      108kB
  + aws-c-mqtt                                    0.11.0  h11f4f37_12                   conda-forge      195kB
  + libgrpc                                       1.67.1  h25350d4_1                    conda-forge        8MB
  + mpc                                            1.3.1  h24ddda3_1                    conda-forge      117kB
  + libheif                                       1.19.5  gpl_hc21c24c_100              conda-forge      589kB
  + libhwloc                                      2.11.2  default_h0d58e46_1001         conda-forge        2MB
  + libxslt                                       1.1.39  h76b75d6_0                    conda-forge      254kB
  + libarchive                                     3.7.7  h4585015_3                    conda-forge      878kB
  + prmon                                          3.1.1  hfb47081_1                    conda-forge      251kB
  + openjpeg                                       2.5.3  h5fbd93e_0                    conda-forge      343kB
  + lcms2                                           2.16  hb7c19ff_0                    conda-forge      245kB
  + rdma-core                                       55.0  h5888daf_0                    conda-forge        1MB
  + cyrus-sasl                                    2.1.27  h54b06d7_7                    conda-forge      220kB
  + zeromq                                         4.3.5  h3b0a872_7                    conda-forge      335kB
  + libcurl                                       8.11.1  h332b0f4_0                    conda-forge      423kB
  + log4cxx                                        1.1.0  ha5ff813_1                    conda-forge      757kB
  + dbus                                          1.13.6  h5008d03_3                    conda-forge      619kB
  + liblapack                                      3.9.0  20_linux64_openblas           conda-forge       14kB
  + libcblas                                       3.9.0  20_linux64_openblas           conda-forge       14kB
  + aws-c-s3                                       0.7.7  hf454442_0                    conda-forge      114kB
  + libpmix                                        5.0.6  h658e747_0                    conda-forge      715kB
  + ucx                                           1.17.0  h53fb5aa_4                    conda-forge        7MB
  + libfabric1                                     2.0.0  h14e6f36_1                    conda-forge      670kB
  + openldap                                       2.6.9  he970967_0                    conda-forge      784kB
  + hdf5                                          1.14.4  nompi_h2d575fe_105            conda-forge        4MB
  + proj                                           9.5.1  h0054346_0                    conda-forge        3MB
  + libmamba                                      1.5.10  h4cc3d14_0                    conda-forge        2MB
  + scitokens-cpp                                  1.1.1  h475ca95_0                    conda-forge        2MB
  + azure-core-cpp                                1.14.0  h5cfcd09_0                    conda-forge      345kB
  + libgoogle-cloud                               2.33.0  h2b5623c_1                    conda-forge        1MB
  + git                                           2.45.2  pl5321he096aa3_0              conda-forge       11MB
  + cmake                                         3.31.2  h74e3db0_1                    conda-forge       20MB
  + cfitsio                                        4.3.1  hbdc6101_0                    conda-forge      875kB
  + libtorch                                       2.5.1  cpu_generic_h213959a_8        conda-forge       53MB
  + liblapacke                                     3.9.0  20_linux64_openblas           conda-forge       14kB
  + gsl                                              2.7  he838d99_0                    conda-forge        3MB
  + aws-crt-cpp                                   0.29.7  hd92328a_7                    conda-forge      355kB
  + ucc                                            1.3.0  h0f835a6_3                    conda-forge        8MB
  + libfabric                                      2.0.0  ha770c72_1                    conda-forge       14kB
  + libpq                                           17.2  h3b95a9b_1                    conda-forge        3MB
  + libcondor_utils                               23.0.3  h5fb16dd_0                    conda-forge       24MB
  + azure-storage-common-cpp                      12.8.0  h736e048_1                    conda-forge      149kB
  + azure-identity-cpp                            1.10.0  h113e628_0                    conda-forge      232kB
  + libgoogle-cloud-storage                       2.33.0  h0121fbd_1                    conda-forge      784kB
  + fitsverify                                      4.22  h6b5e9fc_0                    conda-forge       52kB
  + wcslib                                         8.2.2  h6cde4e1_0                    conda-forge      641kB
  + aws-sdk-cpp                                 1.11.458  hc430e4a_4                    conda-forge        3MB
  + openmpi                                        5.0.6  h3ee89b5_101                  conda-forge        4MB
  + htcondor-utils                                23.0.3  h841b71b_0                    conda-forge       32MB
  + azure-storage-blobs-cpp                      12.13.0  h3cf044e_1                    conda-forge      549kB
  + azure-storage-files-datalake-cpp             12.12.0  ha633028_1                    conda-forge      287kB
  + tzdata                                         2024b  hc8b5060_0                    conda-forge      122kB
  + nomkl                                            1.0  h5ca1d4c_0                    conda-forge        4kB
  + libstdcxx-devel_linux-64                      12.4.0  ha4f9413_101                  conda-forge       12MB
  + libgcc-devel_linux-64                         12.4.0  ha4f9413_101                  conda-forge        3MB
  + pybind11-abi                                       4  hd8ed1ab_3                    conda-forge     Cached
  + kernel-headers_linux-64                       3.10.0  he073ed8_18                   conda-forge      943kB
  + sysroot_linux-64                                2.17  h0157908_18                   conda-forge       15MB
  + orc                                            2.0.3  h12ee42a_2                    conda-forge        1MB
  + python                                       3.11.11  h9e4cc4f_1_cpython            conda-forge       31MB
  + binutils_impl_linux-64                          2.43  h4bf12b8_2                    conda-forge        6MB
  + libarrow                                      18.1.0  hd595efa_7_cpu                conda-forge        9MB
  + binutils                                        2.43  h4852527_2                    conda-forge       34kB
  + gcc_impl_linux-64                             12.4.0  hb2e57f8_1                    conda-forge       62MB
  + binutils_linux-64                               2.43  h4852527_2                    conda-forge       35kB
  + libarrow-acero                                18.1.0  hcb10f89_7_cpu                conda-forge      612kB
  + libparquet                                    18.1.0  h081d1f1_7_cpu                conda-forge        1MB
  + gcc                                           12.4.0  h236703b_1                    conda-forge       54kB
  + gfortran_impl_linux-64                        12.4.0  hc568b83_1                    conda-forge       15MB
  + gxx_impl_linux-64                             12.4.0  h613a52c_1                    conda-forge       13MB
  + gcc_linux-64                                  12.4.0  h6b7512a_7                    conda-forge       32kB
  + libarrow-dataset                              18.1.0  hcb10f89_7_cpu                conda-forge      587kB
  + gfortran                                      12.4.0  h236703b_1                    conda-forge       53kB
  + gxx                                           12.4.0  h236703b_1                    conda-forge       53kB
  + c-compiler                                     1.7.0  hd590300_1                    conda-forge        6kB
  + gfortran_linux-64                             12.4.0  hd748a6a_7                    conda-forge       30kB
  + gxx_linux-64                                  12.4.0  h8489865_7                    conda-forge       30kB
  + libarrow-substrait                            18.1.0  h08228c5_7_cpu                conda-forge      522kB
  + fortran-compiler                               1.7.0  heb67821_1                    conda-forge        6kB
  + cxx-compiler                                   1.7.0  h00ab1b0_1                    conda-forge        6kB
  + compilers                                      1.7.0  ha770c72_1                    conda-forge        7kB
  + wheel                                         0.45.1  pyhd8ed1ab_1                  conda-forge       63kB
  + setuptools                                    71.0.4  pyhd8ed1ab_0                  conda-forge        1MB
  + pip                                           24.3.1  pyh8b19718_2                  conda-forge        1MB
  + cached_property                                1.5.2  pyha770c72_1                  conda-forge       11kB
  + py-cpuinfo                                     9.0.0  pyhd8ed1ab_1                  conda-forge       26kB
  + backports                                        1.0  pyhd8ed1ab_5                  conda-forge        7kB
  + more-itertools                                10.5.0  pyhd8ed1ab_1                  conda-forge       58kB
  + jsonpickle                                     4.0.0  pyh29332c3_0                  conda-forge       45kB
  + pkgutil-resolve-name                          1.3.10  pyhd8ed1ab_2                  conda-forge       11kB
  + pathable                                       0.4.3  pyhd8ed1ab_1                  conda-forge       17kB
  + jeepney                                        0.8.0  pyhd8ed1ab_0                  conda-forge       37kB
  + pyasn1                                         0.6.1  pyhd8ed1ab_2                  conda-forge       62kB
  + types-pyyaml                         6.0.12.20241230  pyhd8ed1ab_0                  conda-forge       21kB
  + pbr                                            6.1.0  pyhd8ed1ab_1                  conda-forge       74kB
  + joblib                                         1.4.2  pyhd8ed1ab_1                  conda-forge      220kB
  + semantic_version                              2.10.0  pyhd8ed1ab_0                  conda-forge       18kB
  + asdf-standard                                  1.1.1  pyhd8ed1ab_1                  conda-forge       35kB
  + jmespath                                       1.0.1  pyhd8ed1ab_1                  conda-forge       24kB
  + humanfriendly                                   10.0  pyh707e725_8                  conda-forge       74kB
  + docopt                                         0.6.2  pyhd8ed1ab_2                  conda-forge       19kB
  + orderly-set                                    5.2.3  pyh29332c3_1                  conda-forge       18kB
  + pywin32-on-windows                             0.1.0  pyh1179c8e_3                  conda-forge        5kB
  + websocket-client                               1.8.0  pyhd8ed1ab_1                  conda-forge       47kB
  + itsdangerous                                   2.2.0  pyhd8ed1ab_1                  conda-forge       19kB
  + hyperframe                                     6.0.1  pyhd8ed1ab_1                  conda-forge       17kB
  + hpack                                          4.0.0  pyhd8ed1ab_1                  conda-forge       29kB
  + tabulate                                       0.9.0  pyhd8ed1ab_2                  conda-forge       38kB
  + argcomplete                                    3.5.2  pyhd8ed1ab_0                  conda-forge       41kB
  + zipp                                          3.21.0  pyhd8ed1ab_1                  conda-forge       22kB
  + parso                                          0.8.4  pyhd8ed1ab_1                  conda-forge       75kB
  + xmltodict                                     0.14.2  pyhd8ed1ab_1                  conda-forge       16kB
  + blinker                                        1.9.0  pyhff2d567_0                  conda-forge       14kB
  + locket                                         1.0.0  pyhd8ed1ab_0                  conda-forge        8kB
  + ptyprocess                                     0.7.0  pyhd8ed1ab_1                  conda-forge       19kB
  + sqlparse                                       0.4.4  pyhd8ed1ab_0                  conda-forge       38kB
  + wcwidth                                       0.2.13  pyhd8ed1ab_1                  conda-forge       33kB
  + cachetools                                     5.5.0  pyhd8ed1ab_1                  conda-forge       15kB
  + iniconfig                                      2.0.0  pyhd8ed1ab_1                  conda-forge       11kB
  + toml                                          0.10.2  pyhd8ed1ab_1                  conda-forge       22kB
  + execnet                                        2.1.1  pyhd8ed1ab_1                  conda-forge       39kB
  + pure_eval                                      0.2.3  pyhd8ed1ab_1                  conda-forge       17kB
  + executing                                      2.1.0  pyhd8ed1ab_1                  conda-forge       28kB
  + asttokens                                      3.0.0  pyhd8ed1ab_1                  conda-forge       28kB
  + cpython                                      3.11.11  py311hd8ed1ab_1               conda-forge       46kB
  + colorama                                       0.4.6  pyhd8ed1ab_1                  conda-forge       27kB
  + pysocks                                        1.7.1  pyha55dd90_7                  conda-forge       21kB
  + aiohappyeyeballs                               2.4.4  pyhd8ed1ab_1                  conda-forge       19kB
  + attrs                                         24.3.0  pyh71513ae_0                  conda-forge       56kB
  + astropy-iers-data                 0.2025.1.6.0.33.42  pyhd8ed1ab_0                  conda-forge        1MB
  + pycparser                                       2.22  pyh29332c3_1                  conda-forge      110kB
  + truststore                                    0.10.0  pyhd8ed1ab_0                  conda-forge       22kB
  + platformdirs                                   4.3.6  pyhd8ed1ab_1                  conda-forge       20kB
  + boltons                                       24.0.0  pyhd8ed1ab_1                  conda-forge      297kB
  + distro                                         1.9.0  pyhd8ed1ab_1                  conda-forge       42kB
  + pluggy                                         1.5.0  pyhd8ed1ab_1                  conda-forge       24kB
  + tomli                                          2.2.1  pyhd8ed1ab_1                  conda-forge       19kB
  + munkres                                        1.1.4  pyh9f0ad1d_0                  conda-forge       12kB
  + pyparsing                                      3.2.1  pyhd8ed1ab_0                  conda-forge       93kB
  + cycler                                        0.12.1  pyhd8ed1ab_1                  conda-forge       13kB
  + python-tzdata                                 2024.2  pyhd8ed1ab_1                  conda-forge      142kB
  + filelock                                      3.16.1  pyhd8ed1ab_1                  conda-forge       17kB
  + threadpoolctl                                  3.5.0  pyhc1e730c_0                  conda-forge       24kB
  + panda-client                                  1.5.82  pyhd8ed1ab_1                  conda-forge      168kB
  + ws4py                                          0.5.1  py_0                          conda-forge       35kB
  + networkx                                       3.4.2  pyh267e887_2                  conda-forge        1MB
  + meson                                          1.6.1  pyhd8ed1ab_0                  conda-forge      657kB
  + humanize                                      4.11.0  pyhd8ed1ab_1                  conda-forge       66kB
  + future                                         1.0.0  pyhd8ed1ab_1                  conda-forge      364kB
  + defusedxml                                     0.7.1  pyhd8ed1ab_0                  conda-forge       24kB
  + configparser                                   7.1.0  pyhd8ed1ab_1                  conda-forge       22kB
  + archspec                                       0.2.3  pyhd8ed1ab_0                  conda-forge     Cached
  + backoff                                        2.2.1  pyhd8ed1ab_1                  conda-forge       19kB
  + soupsieve                                        2.5  pyhd8ed1ab_1                  conda-forge       37kB
  + cloudpickle                                    3.1.0  pyhd8ed1ab_2                  conda-forge       26kB
  + toolz                                          1.0.0  pyhd8ed1ab_1                  conda-forge       52kB
  + click                                          8.1.8  pyh707e725_0                  conda-forge       85kB
  + webencodings                                   0.5.1  pyhd8ed1ab_3                  conda-forge       15kB
  + gast                                           0.4.0  pyh9f0ad1d_0                  conda-forge       12kB
  + nest-asyncio                                   1.6.0  pyhd8ed1ab_1                  conda-forge       12kB
  + packaging                                       24.2  pyhd8ed1ab_2                  conda-forge       60kB
  + pygments                                      2.19.1  pyhd8ed1ab_0                  conda-forge      889kB
  + exceptiongroup                                 1.2.2  pyhd8ed1ab_1                  conda-forge       20kB
  + pickleshare                                    0.7.5  pyhd8ed1ab_1004               conda-forge       12kB
  + decorator                                      5.1.1  pyhd8ed1ab_1                  conda-forge       14kB
  + widgetsnbextension                            4.0.13  pyhd8ed1ab_1                  conda-forge      898kB
  + jupyterlab_widgets                            3.0.13  pyhd8ed1ab_1                  conda-forge      186kB
  + traitlets                                     5.14.3  pyhd8ed1ab_1                  conda-forge      110kB
  + charset-normalizer                             3.4.1  pyhd8ed1ab_0                  conda-forge       47kB
  + idna                                            3.10  pyhd8ed1ab_1                  conda-forge       50kB
  + fsspec                                     2024.12.0  pyhd8ed1ab_0                  conda-forge      138kB
  + mpmath                                         1.3.0  pyhd8ed1ab_1                  conda-forge      440kB
  + certifi                                   2024.12.14  pyhd8ed1ab_0                  conda-forge      162kB
  + sortedcontainers                               2.4.0  pyhd8ed1ab_0                  conda-forge       26kB
  + pytz                                          2024.2  pyhd8ed1ab_1                  conda-forge      186kB
  + pyflakes                                       3.0.1  pyhd8ed1ab_0                  conda-forge       57kB
  + mccabe                                         0.7.0  pyhd8ed1ab_1                  conda-forge       13kB
  + pyjwt                                         2.10.1  pyhd8ed1ab_0                  conda-forge       25kB
  + types-six                            1.17.0.20241205  pyhd8ed1ab_1                  conda-forge       26kB
  + typeguard                                     2.13.3  pyhd8ed1ab_0                  conda-forge       20kB
  + typing_extensions                             4.12.2  pyha770c72_1                  conda-forge       40kB
  + tblib                                          3.0.0  pyhd8ed1ab_1                  conda-forge       17kB
  + dill                                           0.3.9  pyhd8ed1ab_1                  conda-forge       90kB
  + six                                           1.17.0  pyhd8ed1ab_0                  conda-forge       16kB
  + nose                                           1.3.7  py_1006                       conda-forge      121kB
  + pycodestyle                                   2.10.0  pyhd8ed1ab_0                  conda-forge       43kB
  + cached-property                                1.5.2  hd8ed1ab_1                    conda-forge        4kB
  + backports.tarfile                              1.2.0  pyhd8ed1ab_1                  conda-forge       33kB
  + jaraco.functools                               4.1.0  pyhd8ed1ab_0                  conda-forge       16kB
  + jaraco.classes                                 3.4.0  pyhd8ed1ab_2                  conda-forge       12kB
  + rsa                                              4.9  pyhd8ed1ab_1                  conda-forge       31kB
  + stevedore                                      5.4.0  pyhd8ed1ab_1                  conda-forge       32kB
  + asdf-transform-schemas                         0.5.0  pyhd8ed1ab_1                  conda-forge       68kB
  + coloredlogs                                   15.0.1  pyhd8ed1ab_4                  conda-forge       44kB
  + deepdiff                                       8.1.1  pyhd8ed1ab_0                  conda-forge       74kB
  + stomp.py                                       8.2.0  pyhd8ed1ab_0                  conda-forge       39kB
  + h2                                             4.1.0  pyhd8ed1ab_1                  conda-forge       52kB
  + importlib_resources                            6.5.2  pyhd8ed1ab_0                  conda-forge       34kB
  + importlib-metadata                             8.5.0  pyha770c72_1                  conda-forge       29kB
  + jedi                                          0.19.2  pyhd8ed1ab_1                  conda-forge      844kB
  + pexpect                                        4.9.0  pyhd8ed1ab_1                  conda-forge       54kB
  + prompt-toolkit                                3.0.48  pyha770c72_1                  conda-forge      270kB
  + stack_data                                     0.6.3  pyhd8ed1ab_1                  conda-forge       27kB
  + tqdm                                          4.67.1  pyhd8ed1ab_1                  conda-forge       89kB
  + sarif-om                                       1.0.4  pyhd8ed1ab_1                  conda-forge       23kB
  + jschema-to-python                              1.2.3  pyhff2d567_1                  conda-forge       14kB
  + pydot                                          1.2.4  py_0                          conda-forge       21kB
  + beautifulsoup4                                4.12.3  pyha770c72_1                  conda-forge      118kB
  + partd                                          1.4.2  pyhd8ed1ab_0                  conda-forge       21kB
  + bleach                                         6.2.0  pyhd8ed1ab_3                  conda-forge      133kB
  + py2vega                                        0.6.1  pyhd8ed1ab_0                  conda-forge       17kB
  + pytest                                         8.0.2  pyhd8ed1ab_0                  conda-forge      252kB
  + traittypes                                     0.2.1  pyh9f0ad1d_2                  conda-forge       10kB
  + jupyter_core                                   5.7.2  pyh31011fe_1                  conda-forge       58kB
  + matplotlib-inline                              0.1.7  pyhd8ed1ab_1                  conda-forge       14kB
  + comm                                           0.2.2  pyhd8ed1ab_1                  conda-forge       12kB
  + hypothesis                                  6.123.11  pyha770c72_0                  conda-forge      346kB
  + graphql-core                                   3.2.5  pyhd8ed1ab_1                  conda-forge      359kB
  + python-utils                                   3.9.1  pyhff2d567_1                  conda-forge       32kB
  + aioitertools                                  0.12.0  pyhd8ed1ab_1                  conda-forge       25kB
  + typing-extensions                             4.12.2  hd8ed1ab_1                    conda-forge       10kB
  + rfc3339-validator                              0.1.4  pyhd8ed1ab_1                  conda-forge       10kB
  + junit-xml                                        1.9  pyhd8ed1ab_1                  conda-forge       13kB
  + configobj                                      5.0.9  pyhd8ed1ab_1                  conda-forge       38kB
  + python-dateutil                          2.9.0.post0  pyhff2d567_1                  conda-forge      223kB
  + geomet                                   0.2.1.post1  pyh9f0ad1d_0                  conda-forge       23kB
  + html5lib                                         1.1  pyhd8ed1ab_2                  conda-forge       95kB
  + flake8                                         6.0.0  pyhd8ed1ab_0                  conda-forge      109kB
  + jaraco.context                                 6.0.1  pyhd8ed1ab_0                  conda-forge       12kB
  + dogpile.cache                                  1.3.3  pyhd8ed1ab_0                  conda-forge       53kB
  + lazy-loader                                      0.4  pyhd8ed1ab_2                  conda-forge       16kB
  + importlib_metadata                             8.5.0  hd8ed1ab_1                    conda-forge        9kB
  + prompt_toolkit                                3.0.48  hd8ed1ab_1                    conda-forge        7kB
  + pytest-filter-subpackage                       0.2.0  pyhd8ed1ab_0                  conda-forge       11kB
  + pytest-astropy-header                          0.2.2  pyhd8ed1ab_1                  conda-forge       13kB
  + pytest-mock                                   3.14.0  pyhd8ed1ab_1                  conda-forge       22kB
  + pytest-remotedata                              0.4.1  pyhd8ed1ab_0                  conda-forge       14kB
  + pytest-subtests                               0.14.1  pyhd8ed1ab_0                  conda-forge       18kB
  + pytest-session2file                           0.1.11  pyhd8ed1ab_1                  conda-forge       14kB
  + pytest-doctestplus                             1.3.0  pyhd8ed1ab_1                  conda-forge       28kB
  + pytest-xdist                                   3.6.1  pyhd8ed1ab_1                  conda-forge       38kB
  + pytest-runner                                  6.0.0  pyhd8ed1ab_0                  conda-forge       11kB
  + ipython                                       8.31.0  pyh707e725_0                  conda-forge      601kB
  + progressbar2                                   4.5.0  pyhd8ed1ab_1                  conda-forge       55kB
  + setuptools-scm                                 8.1.0  pyhd8ed1ab_1                  conda-forge       38kB
  + annotated-types                                0.7.0  pyhd8ed1ab_1                  conda-forge       18kB
  + cli_helpers                                    2.3.1  pyhd8ed1ab_1                  conda-forge       22kB
  + pep8-naming                                   0.14.1  pyhd8ed1ab_1                  conda-forge       14kB
  + lazy_loader                                      0.4  pyhd8ed1ab_2                  conda-forge        7kB
  + ipywidgets                                     8.1.5  pyhd8ed1ab_1                  conda-forge      114kB
  + mpi4py                                         4.0.1  py311ha982e2a_1               conda-forge      874kB
  + rpds-py                                       0.22.3  py311h9e33e62_0               conda-forge      352kB
  + lazy-object-proxy                             1.10.0  py311h459d7ec_0               conda-forge       41kB
  + ruamel.yaml.clib                               0.2.8  py311h9ecbd09_1               conda-forge      147kB
  + greenlet                                       3.1.1  py311hfdbb021_1               conda-forge      240kB
  + regex                                      2024.11.6  py311h9ecbd09_0               conda-forge      410kB
  + libmambapy                                    1.5.10  py311h7f1ffb1_0               conda-forge      331kB
  + markupsafe                                     3.0.2  py311h2dc5d0c_1               conda-forge       25kB
  + jsonpointer                                    3.0.0  py311h38be061_1               conda-forge       18kB
  + lxml                                           5.3.0  py311hcfaa980_2               conda-forge        1MB
  + gmpy2                                          2.1.5  py311h0f6cedb_3               conda-forge      203kB
  + brotli-python                                  1.1.0  py311hfdbb021_2               conda-forge      350kB
  + propcache                                      0.2.1  py311h9ecbd09_0               conda-forge       53kB
  + multidict                                      6.1.0  py311h2dc5d0c_2               conda-forge       63kB
  + frozenlist                                     1.5.0  py311h9ecbd09_0               conda-forge       61kB
  + menuinst                                       2.2.0  py311h38be061_0               conda-forge      171kB
  + pycosat                                        0.6.6  py311h9ecbd09_2               conda-forge       88kB
  + unicodedata2                                  15.1.0  py311h9ecbd09_1               conda-forge      368kB
  + pillow                                        11.1.0  py311h1322bbf_0               conda-forge       42MB
  + kiwisolver                                     1.4.7  py311hd18a35c_0               conda-forge       72kB
  + psycopg-c                                      3.2.3  py311h83e8966_1               conda-forge      381kB
  + scons                                          4.8.1  py311h38be061_1               conda-forge        3MB
  + pybind11-global                               2.10.4  py311ha3edf6b_0               conda-forge      168kB
  + psycopg2                                       2.9.9  py311h83e8966_2               conda-forge      191kB
  + llvmlite                                      0.43.0  py311h9c9ff8c_1               conda-forge        3MB
  + frozendict                                     2.4.6  py311h9ecbd09_0               conda-forge       31kB
  + fastavro                                      1.10.0  py311h9ecbd09_0               conda-forge      538kB
  + eups                                          2.2.10  py311h38be061_1               conda-forge      555kB
  + wrapt                                         1.17.0  py311h9ecbd09_0               conda-forge       65kB
  + pyyaml                                         6.0.2  py311h9ecbd09_1               conda-forge      213kB
  + debugpy                                       1.8.11  py311hfdbb021_0               conda-forge        3MB
  + tornado                                        6.4.2  py311h9ecbd09_0               conda-forge      856kB
  + pyarrow-core                                  18.1.0  py311h4854187_0_cpu           conda-forge        5MB
  + bcrypt                                         4.2.1  py311h9e33e62_0               conda-forge      255kB
  + setproctitle                                   1.3.4  py311h9ecbd09_0               conda-forge       20kB
  + pyzmq                                         26.2.0  py311h7deb3e3_3               conda-forge      389kB
  + psutil                                         6.1.1  py311h9ecbd09_0               conda-forge      505kB
  + numpy                                         1.24.4  py311h64a7726_0               conda-forge        8MB
  + ruff                                           0.1.7  py311h7145743_0               conda-forge        5MB
  + cffi                                          1.17.1  py311hf29c0ef_0               conda-forge      302kB
  + coverage                                      7.6.10  py311h2dc5d0c_0               conda-forge      375kB
  + pyproj                                         3.7.0  py311h0f98d5a_0               conda-forge      562kB
  + multiprocess                                 0.70.17  py311h9ecbd09_1               conda-forge      351kB
  + pydantic-core                                 2.27.2  py311h9e33e62_0               conda-forge        2MB
  + ruamel.yaml                                  0.18.10  py311h9ecbd09_0               conda-forge      273kB
  + sqlalchemy                                    2.0.36  py311h9ecbd09_0               conda-forge        4MB
  + yarl                                          1.18.3  py311h9ecbd09_0               conda-forge      154kB
  + fonttools                                     4.55.3  py311h2dc5d0c_1               conda-forge        3MB
  + psycopg                                        3.2.3  py311h3204690_1               conda-forge      400kB
  + pybind11                                      2.10.4  py311ha3edf6b_0               conda-forge      184kB
  + pyarrow                                       18.1.0  py311h38be061_0               conda-forge       25kB
  + h5py                                          3.12.1  nompi_py311h5ed33ec_103       conda-forge        1MB
  + pywavelets                                     1.8.0  py311h9f3472d_0               conda-forge        4MB
  + pyerfa                                       2.0.1.5  py311h9f3472d_0               conda-forge      376kB
  + imagecodecs                                2024.9.22  py311h9971d45_2               conda-forge        2MB
  + contourpy                                      1.3.1  py311hd18a35c_0               conda-forge      278kB
  + libboost-python                               1.82.0  py311h92ebd52_3               conda-forge      119kB
  + numexpr                                       2.10.2  py311h38b10cd_100             conda-forge      201kB
  + numba                                         0.60.0  py311h4bc866e_0               conda-forge        6MB
  + iminuit                                       2.30.1  py311hfdbb021_0               conda-forge      507kB
  + hpgeom                                         1.4.0  py311h9f3472d_0               conda-forge       74kB
  + fitsio                                         1.2.4  py311hfd33317_1               conda-forge      691kB
  + esutil                                        0.6.16  py311h7db5c69_0               conda-forge      421kB
  + cassandra-driver                              3.29.2  py311he455363_0               conda-forge        3MB
  + pandas                                         2.2.2  py311h14de704_1               conda-forge       16MB
  + bottleneck                                     1.4.2  py311h9f3472d_0               conda-forge      144kB
  + scipy                                         1.11.4  py311h64a7726_0               conda-forge       16MB
  + zstandard                                     0.23.0  py311hbc35293_1               conda-forge      418kB
  + lsstdesc.coord                                 1.3.0  py311hd18a35c_2               conda-forge       47kB
  + cryptography                                  44.0.0  py311hafd3f86_0               conda-forge        2MB
  + pynacl                                         1.5.0  py311h9ecbd09_4               conda-forge        1MB
  + schwimmbad                                     0.4.2  py311h38be061_1               conda-forge       32kB
  + astropy-base                                   7.0.0  py311h2a3ca71_3               conda-forge       10MB
  + matplotlib-base                                3.8.4  py311ha4ca890_2               conda-forge        8MB
  + libboost-python-devel                         1.82.0  py311h781c19f_3               conda-forge       16kB
  + python-htcondor                               23.0.3  py311h949af2a_0               conda-forge        8MB
  + pytables                                      3.10.2  py311h3ebe2b2_0               conda-forge        2MB
  + spherematch                                   0.10.2  py311h9f3472d_2               conda-forge       49kB
  + scikit-learn                                   1.6.0  py311h57cc02b_0               conda-forge       11MB
  + treecorr                                       4.3.3  py311hb755f60_1               conda-forge        1MB
  + secretstorage                                  3.3.3  py311h38be061_3               conda-forge       32kB
  + galsim                                         2.6.3  py311h8f85c52_1               conda-forge        6MB
  + htcondor                                      23.0.3  py311h38be061_0               conda-forge       22kB
  + ngmix-core                                     2.3.2  py311h38be061_0               conda-forge      440kB
  + referencing                                   0.35.1  pyhd8ed1ab_1                  conda-forge       42kB
  + mako                                           1.3.8  pyhd8ed1ab_0                  conda-forge       67kB
  + werkzeug                                       3.1.3  pyhd8ed1ab_1                  conda-forge      244kB
  + jinja2                                         3.1.5  pyhd8ed1ab_0                  conda-forge      113kB
  + jsonpatch                                       1.33  pyhd8ed1ab_1                  conda-forge       17kB
  + ecdsa                                         0.19.0  pyhd8ed1ab_1                  conda-forge      127kB
  + sympy                                         1.13.3  pyh2585a3b_105                conda-forge        5MB
  + aiosignal                                      1.3.2  pyhd8ed1ab_0                  conda-forge       13kB
  + deprecated                                    1.2.15  pyhd8ed1ab_1                  conda-forge       14kB
  + jsondiff                                       2.2.1  pyhd8ed1ab_1                  conda-forge       18kB
  + dask-core                                  2024.12.1  pyhd8ed1ab_0                  conda-forge      906kB
  + jupyter_client                                 8.6.3  pyhd8ed1ab_1                  conda-forge      106kB
  + pytest-openfiles                               0.5.0  pyhd8ed1ab_1                  conda-forge       12kB
  + imageio                                       2.36.1  pyh12aca89_1                  conda-forge      292kB
  + patsy                                          1.0.1  pyhd8ed1ab_1                  conda-forge      187kB
  + asdf                                           4.0.0  pyhd8ed1ab_1                  conda-forge      501kB
  + asteval                                        1.0.5  pyhd8ed1ab_0                  conda-forge       25kB
  + uncertainties                                  3.2.2  pyhd8ed1ab_2                  conda-forge       56kB
  + pytest-arraydiff                               0.6.1  pyhd8ed1ab_0                  conda-forge       15kB
  + emcee                                          3.1.6  pyhd8ed1ab_1                  conda-forge       40kB
  + jplephem                                        2.21  pyh9b8db34_1                  conda-forge       39kB
  + pytest-cov                                     6.0.0  pyhd8ed1ab_1                  conda-forge       26kB
  + pydantic                                      2.10.4  pyh3cfb1c2_0                  conda-forge      297kB
  + vcrpy                                          7.0.0  pyhd8ed1ab_0                  conda-forge       39kB
  + pgspecial                                      2.1.3  pyhd8ed1ab_1                  conda-forge       38kB
  + tifffile                                  2024.12.12  pyhd8ed1ab_0                  conda-forge      181kB
  + bqplot                                       0.12.43  pyhd8ed1ab_1                  conda-forge      864kB
  + autograd                                       1.6.2  pyhd8ed1ab_0                  conda-forge       45kB
  + conda-package-streaming                       0.11.0  pyhd8ed1ab_0                  conda-forge       21kB
  + urllib3                                        2.3.0  pyhd8ed1ab_0                  conda-forge      100kB
  + types-paramiko                        3.5.0.20240928  pyhd8ed1ab_1                  conda-forge       36kB
  + paramiko                                       3.5.0  pyhd8ed1ab_1                  conda-forge      161kB
  + lsst-ts-xml                                   22.1.1  pyh707e725_0                  conda-forge      285kB
  + healsparse                                    1.10.1  pyhd8ed1ab_1                  conda-forge       55kB
  + seaborn-base                                  0.13.2  pyhd8ed1ab_3                  conda-forge      228kB
  + treegp                                         1.2.0  pyhd8ed1ab_1                  conda-forge       24kB
  + keyring                                       25.6.0  pyha804496_0                  conda-forge       37kB
  + jsonschema-specifications                  2023.12.1  pyhd8ed1ab_0                  conda-forge       16kB
  + alembic                                       1.14.0  pyhd8ed1ab_1                  conda-forge      159kB
  + flask                                          3.1.0  pyhff2d567_0                  conda-forge       81kB
  + sshpubkeys                                     3.3.1  pyhd8ed1ab_1                  conda-forge       16kB
  + python-jose                                    3.3.0  pyhff2d567_2                  conda-forge      106kB
  + ipykernel                                     6.29.5  pyh3099207_0                  conda-forge      119kB
  + asdf-coordinates-schemas                       0.3.0  pyhd8ed1ab_1                  conda-forge       19kB
  + lmfit                                          1.2.2  pyhd8ed1ab_1                  conda-forge       84kB
  + pytest-astropy                                0.11.0  pyhd8ed1ab_0                  conda-forge       11kB
  + pytest-vcr                                     1.0.2  pyhd8ed1ab_1                  conda-forge       10kB
  + pgcli                                          4.1.0  pyhd8ed1ab_1                  conda-forge       77kB
  + ipydatagrid                                    1.4.0  pyhd8ed1ab_1                  conda-forge      620kB
  + botocore                                     1.35.88  pyge310_1234567_0             conda-forge        8MB
  + types-requests                       2.32.0.20241016  pyhd8ed1ab_1                  conda-forge       26kB
  + requests                                      2.32.3  pyhd8ed1ab_1                  conda-forge       59kB
  + skyproj                                        1.2.4  pyh2cfa8aa_1                  conda-forge        3MB
  + jsonschema                                    4.23.0  pyhd8ed1ab_1                  conda-forge       74kB
  + flask_cors                                     4.0.0  pyhd8ed1ab_0                  conda-forge       18kB
  + asdf-wcs-schemas                               0.4.0  pyhd8ed1ab_1                  conda-forge       21kB
  + s3transfer                                    0.10.4  pyhd8ed1ab_1                  conda-forge       63kB
  + aws-xray-sdk                                  2.14.0  pyhd8ed1ab_1                  conda-forge       73kB
  + jsonschema-path                                0.3.3  pyhd8ed1ab_1                  conda-forge       18kB
  + pyvo                                             1.6  pyhd8ed1ab_2                  conda-forge      847kB
  + responses                                     0.25.3  pyhd8ed1ab_1                  conda-forge       51kB
  + docker-py                                      7.1.0  pyhd8ed1ab_1                  conda-forge      104kB
  + conda-package-handling                         2.4.0  pyh7900ff3_2                  conda-forge      258kB
  + pyld                                           2.0.4  pyhd8ed1ab_1                  conda-forge       65kB
  + idds-common                                   2.1.37  pyhd8ed1ab_0                  conda-forge       30kB
  + firefly-client                                 3.2.0  pyhd8ed1ab_0                  conda-forge       34kB
  + coveralls                                      4.0.1  pyhd8ed1ab_1                  conda-forge       19kB
  + globus-sdk                                    3.49.0  pyhd8ed1ab_0                  conda-forge      234kB
  + openapi-schema-validator                       0.6.2  pyhd8ed1ab_1                  conda-forge       18kB
  + boto3                                        1.35.88  pyhd8ed1ab_0                  conda-forge       83kB
  + astroquery                                     0.4.7  pyhd8ed1ab_2                  conda-forge        4MB
  + idds-workflow                                 2.1.37  pyhd8ed1ab_0                  conda-forge       52kB
  + parsl                                      2023.6.12  pyhd8ed1ab_0                  conda-forge      273kB
  + openapi-spec-validator                         0.7.1  pyhd8ed1ab_1                  conda-forge       42kB
  + aws-sam-translator                            1.94.0  pyhd8ed1ab_1                  conda-forge      258kB
  + idds-doma                                     2.1.37  pyhd8ed1ab_0                  conda-forge       31kB
  + idds-client                                   2.1.37  pyhd8ed1ab_0                  conda-forge       24kB
  + cfn-lint                                      1.22.3  pyhd8ed1ab_0                  conda-forge        1MB
  + moto                                          4.2.14  pyhd8ed1ab_0                  conda-forge        2MB
  + pytorch                                        2.5.1  cpu_generic_py311_h740418c_8  conda-forge       38MB
  + aiohttp                                      3.11.11  py311h2dc5d0c_0               conda-forge      923kB
  + statsmodels                                   0.14.4  py311h9f3472d_0               conda-forge       12MB
  + scikit-image                                  0.25.0  py311h7db5c69_1               conda-forge       11MB
  + piff                                           1.3.3  py311h38be061_1               conda-forge      259kB
  + conda                                        24.11.2  py311h38be061_1               conda-forge        1MB
  + torchvision                                   0.20.1  cpu_py311_hc089280_4          conda-forge        1MB
  + aiobotocore                                   2.16.1  pyhd8ed1ab_0                  conda-forge       67kB
  + seaborn                                       0.13.2  hd8ed1ab_3                    conda-forge        7kB
  + conda-libmamba-solver                         24.9.0  pyhd8ed1ab_0                  conda-forge       42kB
  + s3fs                                       2024.12.0  pyhd8ed1ab_0                  conda-forge       33kB
  + astropy                                        7.0.0  pyhd8ed1ab_3                  conda-forge        8kB
  + asdf-astropy                                   0.7.0  pyhd8ed1ab_0                  conda-forge       59kB
  + getcalspec                                     2.1.0  pyhd8ed1ab_1                  conda-forge       20kB
  + gwcs                                          0.21.0  pyhd8ed1ab_2                  conda-forge      125kB
  + pysynphot                                      2.0.0  py311h1f0f07a_6               conda-forge        3MB
  + healpy                                        1.16.6  py311h927b5fe_2               conda-forge        3MB
  + photutils                                      1.8.0  py311h1f0f07a_0               conda-forge      793kB
  + dustmaps                                      1.0.13  py311h38be061_2               conda-forge      737kB
  + rubin-env-nosysroot                            8.0.0  py311he500301_16              conda-forge       14kB
  + rubin-env                                      8.0.0  py311h38be061_16              conda-forge       10kB


The conda environments aren't matched. Have till end of Jan for Stampede storage. Should be good.

How to do nightly coadds?

$ nights=$(echo $DEEP_PROJECT_DIR/repo/DEEP/[0-9]*[0-9] | tr ' ' '\n' | awk -F"/" '{print $NF}')
$ echo "$nights" | xargs -I % python bin/warps.py $REPO % --collections DEEP/%/drp --where "instrument='DECam' and detector!=31"

python bin/pipeline.py $REPO coadd "[0-9]+"

Should I exclude detector 31 from the input warps? I didn't do this for the all sky coadd...this excludes ~1% of the warps for 20190401. That's < 1/62

$ python bin/warps.py $REPO 20190401 --collections DEEP/20190401/drp 
INFO:__main__:associatating 23302 of deepCoadd_psfMatchedWarp into DEEP/20190401/coadd/warps
INFO:__main__:associatating 23302 of deepCoadd_directWarp into DEEP/20190401/coadd/warps

$ python bin/warps.py $REPO 20190401 --collections DEEP/20190401/drp --where "instrument='DECam' and detector!=31"
INFO:__main__:associatating 23091 of deepCoadd_psfMatchedWarp into DEEP/20190401/coadd/warps
INFO:__main__:associatating 23091 of deepCoadd_directWarp into DEEP/20190401/coadd/warps

$ python bin/warps.py $REPO 20190401 --collections DEEP/20190401/drp --where "instrument='DECam' and detector not in (31, 61)"

$ python bin/warps.py $REPO 20190401 --collections DEEP/20190401/drp --where "instrument='DECam' and detector not in (31, 61)"
INFO:__main__:associatating 23071 of deepCoadd_psfMatchedWarp into DEEP/20190401/coadd/warps
INFO:__main__:associatating 23071 of deepCoadd_directWarp into DEEP/20190401/coadd/warps


$ echo "$nights" | xargs -I % python bin/warps.py $REPO % --collections DEEP/%/drp --where "instrument='DECam' and detector not in (31, 61)" > $DEEP_PROJECT_DIR/processing/stampede/coadds/nightly_warps.log

Rsync doesn't work, but 

[stampede] $ PGHOST="localhost" PGPORT=55432 PGUSER="stevengs" pg_dumpall -f dump.sql
[epyc] 
$ initdb -D ${PG_DATA_PATH}
$ escaped_path=$(printf "'%s'\n" "$PG_DATA_PATH" | sed -e 's/[\/&]/\\&/g')
$ sed --in-place "s/#unix_socket_directories.*/unix_socket_directories = ${escaped_path}/g" ${PG_DATA_PATH}/postgresql.conf
$ sed --in-place "s/#port.*/port = ${PG_PORT}/g" ${PG_DATA_PATH}/postgresql.conf
$ sed --in-place "s/max_connections.*/max_connections = 8192/g" ${PG_DATA_PATH}/postgresql.conf
$ sed --in-place "s/#listen_addresses.*/listen_addresses = '*'/g" ${PG_DATA_PATH}/postgresql.conf

# allow all connections as anyone to any database on any interface
$ echo "host    all             all             0.0.0.0/0               trust" >> ${PG_DATA_PATH}/pg_hba.conf

$ PGPORT=55432 PGHOST=localhost psql postgres < dump.sql

seems to work

So just dump and copy the dump.sql 