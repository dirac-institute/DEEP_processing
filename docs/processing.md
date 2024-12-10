# Defects

BPM are take from `/sdf/group/rubin/datasets/decam/_internal/calib/bpmDes/2014-12-05` on USDF.

```
$ python ./bin/defects.py ./repo ./data/bpm
```

# Refcats

# Fakes

```
$ cd data/fakes
$ python merge.py
$ cd ../../
$ python bin/fakes.py ./repo ./data/fakes/ingest.fits --collection DEEP/fakes
```

# Primitives

1) Ingest: ingests downloaded and valid raws from the exposure database into DECam/raw/all
```
$ python bin/ingest.py ./data/exposures.ecsv -b ./repo --image-dir ./data/images --select night=20190402 obs_type='zero'
sub selecting night=20190402
sub selecting obs_type=zero
INFO:__main__:ingesting 25 files into DECam/raw/all
```

2) Raw: tag raws from DECam/raw/all into RUN collection DEEP/{night}/{proc_type}/raw
```
$ python bin/raw.py ./repo bias 20190402
INFO:__main__:associatating 1550 raws into DEEP/20190402/bias/raw
```

3) Collection: Create CHAINED collection DEEP/{night}/{proc_type} from any in DEEP/{night}/{proc_type}/* as well using a pre-determined set of input collections depending on proc_type
```
$ python bin/collection.py ./repo bias 20190402
INFO:__main__:setting DEEP/20190402/bias to chain ['DECam/calib', 'DEEP/20190402/bias/raw']
```

4) Visit: Define visits from exposures
```
$ butler define-visits ./repo lsst.obs.decam.DarkEnergyCamera --collections DEEP/20190402/bias
lsst.defineVisits INFO: Preprocessing data IDs.
lsst.defineVisits INFO: Registering visit_system 2: by-seq-start-end.
lsst.defineVisits INFO: Registering visit_system 0: one-to-one.
lsst.defineVisits INFO: Grouping 25 exposure(s) into visits.
lsst.defineVisits INFO: Computing regions and other metadata for 25 visit(s).
```

5) Qgraph: test if a pipeline needs to be execute by skipping previous failures
```
$ python bin/qgraph.py -b ./repo -i DEEP/20190402/bias --output-run dummy -p ./pipelines/DEEP-bias.yaml#step1 -d instrument='DECam' and detector=57 --skip-existing-in DEEP/20190402/bias --skip-failures
there are 25 tasks
```
Generate the quantum graph
```
$ pipetask --long-log --log-level VERBOSE qgraph -b ./repo -p ./pipelines/DEEP-bias.yaml#step1 -i DEEP/20190402/bias --output-run DEEP/20190402/bias/DEEP-bias/step1/20241111T115007Z --save-qgraph /epyc/data3/stevengs/proc_lsst/scrubbed/tmp/DEEP_20190402_bias_DEEP-bias_step1_20241111T115007Z.qgraph --qgraph-datastore-records -d instrument='DECam' and detector=57 --skip-existing-in DEEP/20190402/bias
```
6) Submit: Submit a pipeline for execution via BPS. Uses Parsl by default.
```
$ bps --long-log --log-level VERBOSE submit ./pipelines/submit.yaml -b ./repo -i DEEP/20190402/bias --output-run DEEP/20190402/bias/DEEP-bias/step1/20241111T115007Z --qgraph /epyc/data3/stevengs/proc_lsst/scrubbed/tmp/DEEP_20190402_bias_DEEP-bias_step1_20241111T115007Z.qgraph
```

7) Collection: update chain with previous run
```
$ python bin/collection.py ./repo bias 20190402
setting DEEP/20190402/bias = ['DEEP/20190402/bias/DEEP-bias/step1/20241111T115007Z', 'DECam/calib', 'DEEP/20190402/bias/raw']
```

8) Decertify: 
```
$ python bin/decertify.py ./repo DEEP/20190402/calib/bias bias

```

9) Certify:
```
$ butler certify-calibrations ./repo DEEP/20190402/bias DEEP/20190402/calib/bias bias --begin-date 2000-01-01T00:00:00 --end-date 2050-01-01T00:00:00
```

# Groups

- Execute: Execute a pipeline on an input collection chain using Parsl. Encapsulates steps 5, 6, 7
```
$ python bin/execute.py ./repo DEEP/20190402/bias --pipeline ./pipelines/DEEP-bias.yaml#step1 --where "instrument='DECam' and detector=57"
```

- Pipeline: Execute sequential steps of a pipeline on an input collection chain using Parsl. Calls `execute.py` and `collection.py` to execute a sequence of steps in a pre-determined pipeline. Pipeline YAML are determined from the provided proc_type.
```
$ python bin/pipeline.py ./repo bias --nights 20190402 --steps step1 step2
```

- Night: Executes steps 1-9 via `pipeline.py` on data subsets using Parsl. Can constrain processing using dimensions from the exposure database (night) or butler (exposure, detector, band etc.)
```
$ python bin/night.py ./repo ./data/exposures.ecsv --nights 20190402 --where "instrument='DECam' and detector=57"
```

# Survey processing

```
$ python bin/night.py ./repo ./data/exposures.ecsv
$ python bin/warps.py ./repo allSky --collections DEEP/*/drp
$ python bin/coadd.py $REPO allSky
$ python bin/pipeline.py $REPO coadd allSky --steps assembleCoadd
$ python bin/diff.py ./repo 20190402 --coadd-subset allSky

$ python bin/collection.py $REPO diff_drp 20190402 --coadd-subset allSky
$ python bin/pipeline.py $REPO diff_drp 20190402 --coadd-subset allSky --steps step4a
```

Diff semantics are weird. Because we want to target an input calexp subset and a target coadd as well. I'll get to it on Klone...

```
python bin/warps.py ./repo 201904 --collections "DEEP/201904*/drp"
python bin/collection.py $REPO coadd 201904
sbatch --time 18:00:00 --partition skx ./processing/stampede/skx_dev_med.sh python bin/pipeline.py $REPO coadd 201904 --steps assembleCoadd
```

For full all-sky, will probably want to separate out processing by tract or create the qgraph in advance...

I wonder if you can create the qgraph in advance on another machine...because it should just be database queries

The missing data problem should be handled by just one script, after running everything else...

e.g. 2019-05-05 VR and r band flats are missing
use the data from the night before?