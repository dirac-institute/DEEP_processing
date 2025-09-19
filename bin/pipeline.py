"""
Runs a pipeline via bin/execute.py uniformly over a set of nights

The choice is:
- run locally in processes, e.g. Popen
- run via slurm submits

inputs: 
- nights: regex match against collections in the butler
- {bias, flat, science}
- steps: execute these steps in order
- where: data query

for night in nights:
    for step in steps:
        python ./bin/execute.py ./repo DEEP/{night}/bias --pipeline ./pipelines/DEEP-bias.yaml#{step} --where {where}

Perhaps this should be a parsl workflow that targets local resources or slurm? Because there is an implicit dependency graph
and a set of command line commands to run
"""
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)

pipelines = dict(
    bias="DEEP-bias.yaml",
    flat="DEEP-flat.yaml",
    science="DEEP-science.yaml",
    drp="DEEP-DRP.yaml",
    coadd={
        "mean": "DEEP-mean-template.yaml",
        "median": "DEEP-median-template.yaml",
        "meanclip": "DEEP-meanclip-template.yaml",
        "min": "DEEP-min-template.yaml",
        "": "DEEP-template.yaml",
        None: "DEEP-template.yaml",
    },
    diff_drp="DEEP-DRP.yaml",
)

import parsl
from parsl import bash_app
from parsl.executors import HighThroughputExecutor
from deep.parsl import EpycProvider, KloneA40Provider, run_command
from functools import partial

def main():
    import argparse
    import lsst.daf.butler as dafButler
    from lsst.daf.butler.registry import CollectionType
    import re
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("proc_type")
    parser.add_argument("subset") # to support coadd/diff_drp replace nights with subset and add template-type and coadd-subset as an option...
    parser.add_argument("--template-type", default="")
    parser.add_argument("--coadd-subset", default="")
    parser.add_argument("--steps", nargs="+", default=[])
    parser.add_argument("--where")
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--slurm", action="store_true")
    parser.add_argument("--workers", "-J", type=int, default=4)

    args = parser.parse_args()
    
    logging.getLogger().setLevel(args.log_level)

    htex_label = "htex"
    executor_kwargs = dict()
    
    if args.slurm:
        provider = KloneA40Provider(max_blocks=args.workers)
    else:
        provider = EpycProvider(max_blocks=1)
        executor_kwargs = dict(
            max_workers=args.workers
        )
    
    executor_kwargs['provider'] = provider
    config = parsl.Config(
        executors=[
            HighThroughputExecutor(
                label=htex_label,
                **executor_kwargs,
            )
        ],
        run_dir=os.path.join("runinfo", "pipeline"),
    )
    parsl.load(config)

    butler = dafButler.Butler(args.repo)
    collections = butler.registry.queryCollections(
        re.compile(
            os.path.normpath(f"DEEP/{args.subset}/{args.coadd_subset}/{args.template_type}/{args.proc_type}")
        ), 
        collectionTypes=CollectionType.CHAINED
    )

    pipeline = pipelines[args.proc_type]
    if args.proc_type == "coadd":
        pipeline = pipeline[args.template_type]
    futures = []
    for collection in collections:
        l = collection.split("/")
        subset = l[1]
        # _, night, _ = collection.split("/")
        inputs = []
        for step in args.steps:
            cmd = [
                "python",
                f"{os.environ.get('DEEP_PROJECT_DIR')}/bin/collection.py",
                args.repo,
                args.proc_type,
                subset,
            ]
            if args.template_type:
                cmd += ["--template-type", args.template_type]
            if args.coadd_subset:
                cmd += ["--coadd-subset", args.coadd_subset]

            cmd = " ".join(map(str, cmd))
            func = partial(run_command)
            setattr(func, "__name__", f"collection_{subset}_{args.proc_type}_{step}")
            future = bash_app(func)(cmd, inputs=inputs)
            inputs = [future]
            futures.append(future)

            cmd = [
                "python",
                f"{os.environ.get('DEEP_PROJECT_DIR')}/bin/execute.py",
                args.repo,
                collection,
                "--pipeline", f"{os.environ.get('DEEP_PROJECT_DIR')}/pipelines/{pipeline}#{step}",
            ]
            if args.where:
                cmd += [f"--where \"{args.where}\""]
            cmd = " ".join(map(str, cmd))
            func = partial(run_command)
            setattr(func, "__name__", f"execute_{subset}_{args.proc_type}_{step}")
            future = bash_app(func)(cmd, inputs=inputs)
            inputs = [future]
            futures.append(future)
            # put final job in here?
            # in case the final job never ran...?
            cmd = [
                "python",
                f"{os.environ.get('DEEP_PROJECT_DIR')}/bin/collection.py",
                args.repo,
                args.proc_type,
                subset,
            ]
            if args.template_type:
                cmd += ["--template-type", args.template_type]
            if args.coadd_subset:
                cmd += ["--coadd-subset", args.coadd_subset]
            cmd = " ".join(map(str, cmd))
            func = partial(run_command)
            setattr(func, "__name__", f"collection_{subset}_{args.proc_type}_{step}")
            future = bash_app(func)(cmd, inputs=inputs)
            inputs = [future]
            futures.append(future)
    
    for future in futures:
        if future:
            future.exception()

    parsl.dfk().cleanup()

if __name__ == "__main__":
    main()

