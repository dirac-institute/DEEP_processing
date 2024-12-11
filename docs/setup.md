# Environment

Ensure `opt_lsst` and `proc_lsst` is available. Should be set up per-host in `etc`.

Create a python virtual environment:
```
$ source bin/setup.sh
$ python -m pip install --target ./env --no-deps ./modules/parsl
```

# Exposures

```bash
$ python ./bin/exposures.py ./data
$ python bin/exposures_object_raw.py ./data/exposures.ecsv ./data/exposures_object_raw.ecsv
$ python bin/download.py ./data/exposures.ecsv --download-dir ./data/images
```

# Fakes

```
$ cd ./data/fakes
$ python derive.py
```

# Refcats

```
$ python bin/refcats.py ./data/exposures.ecsv
```

# Initial repository setup

On Eypc:
```
$ source bin/setup.sh
$ export REPO="./init_repo"
$ bash ./bin/create_db.sh ${REPO} 55432 deep
$ ./bin/db_ctl.sh $REPO start
$ butler register-instrument ${REPO} lsst.obs.decam.DarkEnergyCamera
$ butler write-curated-calibrations ${REPO} lsst.obs.decam.DarkEnergyCamera
$ butler register-skymap ${REPO} -c name='discrete'
$ bash ./bin/ingest_refcats.sh # ingest refcats for images
$ python ./bin/defects.py ${REPO} ./data/bpm # get defects
$ python ./bin/fakes.py ${REPO} ./data/fakes/derived/ingest.fits --collection DEEP/fakes
$ ./bin/db_ctl.sh $REPO stop
$ cp -r $REPO init_repo.bak # make a backup of the repository
```

# Processing on Stampede

```
$ ssh stetzler@stampede3.tacc.utexas.edu
$ mkdir -p $SCRATCH/data/stampede
$ cd $SCRATCH
$ git clone git@github.com:dirac-institute/DEEP_processing.git
$ echo $SCRATCH
/scratch/10000/stetzler
```

Copy over the images:
```
$ rsync -avL ./data/images/ stetzler@stampede3.tacc.utexas.edu:/scratch/10000/stetzler/data/stampede
```

Copy over the modules
```
$ rsync -avL ./modules stetzler@stampede3.tacc.utexas.edu:/scratch/10000/stetzler/DEEP_processing/.
```

Copy over credentials
```
$ scp ./data/credentials stetzler@stampede3.tacc.utexas.edu:/scratch/10000/stetzler/DEEP_processing/data/credentials
```

Create env on Stampede:
```
$ cd $SCRATCH/DEEP_processing
$ source bin/setup.sh
$ python -m pip install --target ./env --no-deps ./modules/parsl
```

Copy over the initial repository:
```
$ rsync -avL ./init_repo.bak stetzler@stampede3.tacc.utexas.edu:/scratch/10000/stetzler/DEEP_processing/.
$ ssh stetzler@stampede3.tacc.utexas.edu
$ cd $SCRATCH/DEEP_processing
$ cp -r ./init_repo.bak ./repo
```

Set up image directory:
```
$ ssh stetzler@stampede3.tacc.utexas.edu
$ cd $SCRATCH/DEEP_processing
$ ln -s $SCRATCH/data/stampede ./data/images
```

Set up postgres on Stampede:
```
$ ssh stetzler@stampede3.tacc.utexas.edu
$ mamba create -n postgres postgresql=13
$ mamba activate postgres
$ which pg_ctl # copy this over to etc/stampede3.tacc.utexas.edu/setup.sh and append to path
```

## Start a run

```
# get a compute node to work on
$ sbatch /home1/10000/stetzler/start_vscode.sh 
$ squeue --name vs-code-tunnel # get node 
$ ssh <node>
$ cd $SCRATCH/DEEP_processing
$ source bin/setup.sh
$ ./bin/db_ctl.sh ./repo start
```

Job submit scripts: Local run
```bash
#!/usr/bin/env bash
#SBATCH --partition=skx-dev
#SBATCH --time=2:00:00
#SBATCH --nodes=1

w=$SCRATCH/DEEP_processing
cd $w
source ./bin/setup.sh

export PROC_LSST_SITE="local"
export J=48
./bin/db_ctl.sh ./repo start
$@ # e.g. python $w/bin/ingest.py ./data/exposures.ecsv -b ./repo
./bin/db_ctl.sh ./repo stop
```

Considerations:
- submit to skx for 48:00:00
- Have 48 cores for: postgres/parsl submissions/qgraph
- --workers determines the number of simultaneous submissions/qgraphs

Name             MinNode  MaxNode     MaxWall  MaxNodePU  MaxJobsPU   MaxSubmit
icx                    1       32  2-00:00:00         48         12          20
pvc                    1        4  2-00:00:00          4          2           4
skx                    1      256  2-00:00:00        384         40          60
skx-dev                1       16    02:00:00         16          1           3
spr                    1       32  2-00:00:00        180         24          36

skx: max nodes per job 256, per user 384, jobs per user 40, max submit 60

Main: 1 job 1 node
39/59 jobs remain and 383 nodes

So I can do 39 submissions each with 9 nodes

MAX_BLOCK=39 NODES=9 python bin/night.py --workers 1 # 1 submission at a time with up to 39*9=351 nodes each
MAX_BLOCK=1 NODES=9 python bin/night.py --workers 39 # 39 submissions at a time with up to 9 nodes each

Setting nodes high only makes sense for very wide qgraphs otherwise we are wasting SU...we probably want the lowest nodes per block to scale SU properly
9*48=432 cores

Probably something in the middle like
MAX_BLOCKS=9 NODES=4 python bin/night.py --workers 4 # 4 submissions at a time each with up to 9 jobs = 36 running jobs each with 192 cores per job. 

Unfortunately, the way this works we rely on elastic scaling, which doesn't seem feasible unless we use the spr queue.

Otherwise the job is just sitting there for 2 days waiting for the nodes to become available. 2*48 = 192 SU

We have 3058 SU available

I could make calibrations on Klone/Epyc for the whole survey...and then copy all of that over...instead of wasting compute time on doing that again

The most conservative way to do this is:
Get a master SKX node and execute one night at a time using Multi queue:
MAX_BLOCKS=10 NODES=4 PROC_LSST_SITE=multi_stampede python night.py --workers 1
- Local with 48 cores
- SKX with MAX_BLOCKS and NODES

So that we can process a single night and scale out as needed

```bash
#!/usr/bin/env bash
#SBATCH --partition=skx
#SBATCH --time=24:00:00
#SBATCH --nodes=1

w=$SCRATCH/DEEP_processing
cd $w
source ./bin/setup.sh

export PROC_LSST_SITE="stampede"
export PROC_LSST_QUEUE="multi"
export PROC_LSST_MULTI_QUEUES="local,skx"
export PROC_LSST_NODES_PER_BLOCK=4
export PROC_LSST_CORES_PER_NODE=48
export PROC_LSST_MAX_BLOCKS=10
export J=20 # local
./bin/db_ctl.sh ./repo start
python $w/bin/night.py ./repo ./data/exposures.ecsv --nights "20190401|20190402" --workers 2
./bin/db_ctl.sh ./repo stop
```

The queue penalizes short running jobs...so should I scale number of nodes etc so that we have a 15 minute minimum runtime?

```bash
#!/usr/bin/env bash
#SBATCH --partition=skx-dev
#SBATCH --time=00:00:15
#SBATCH --nodes=1

w=$SCRATCH/DEEP_processing

function cleanup() {
    $w/bin/db_ctl.sh $w/repo stop
}

trap cleanup SIGINT
trap cleanup SIGTERM

cd $w
source ./bin/setup.sh

export PROC_LSST_SITE="stampede"
export PROC_LSST_QUEUE="skx"
# export PROC_LSST_MULTI_QUEUES="local,skx"
export PROC_LSST_NODES_PER_BLOCK=1
# export PROC_LSST_CORES_PER_NODE=48
export PROC_LSST_MAX_BLOCKS=1
export J=20 # local
./bin/db_ctl.sh ./repo start
# python $w/bin/night.py ./repo ./data/exposures.ecsv --nights "20190401|20190402" --workers 2
$@
./bin/db_ctl.sh ./repo stop
```