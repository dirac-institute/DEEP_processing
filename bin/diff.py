"""
"""
import parsl
from parsl import bash_app
from parsl.executors import HighThroughputExecutor
from functools import partial
from deep.parsl import run_command
from deep.parsl import EpycProvider, KloneAstroProvider, KloneA40Provider, run_command
from subprocess import Popen, PIPE
import selectors
import sys
import atexit

processes = []

def cleanup():
    for p in processes:
        p.kill()

atexit.register(cleanup)

def popen(*args, **kwargs):
    global processes
    p = Popen(*args, **kwargs)
    # p = Popen("echo", **kwargs)
    print("popen: " + " ".join(*args), file=sys.stderr)
    processes.append(p)
    return p

def _print(p):
    sel = selectors.DefaultSelector()
    sel.register(p.stdout, selectors.EVENT_READ)
    sel.register(p.stderr, selectors.EVENT_READ)

    while True:
        for key, _ in sel.select():
            data = key.fileobj.read1().decode()
            if not data:
                return p
            if key.fileobj is p.stdout:
                print(data, end="")
            else:
                print(data, end="", file=sys.stderr)

def run_and_pipe(*args, **kwargs):
    if 'stdout' not in kwargs:
        kwargs['stdout'] = PIPE
    if 'stderr' not in kwargs:
        kwargs['stderr'] = PIPE
    p = popen(*args, **kwargs)
    return _print(p)

def main():
    import argparse
    import os
    import lsst.daf.butler as dafButler
    from lsst.daf.butler.registry import CollectionType
    import re

    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("subset")
    parser.add_argument("--coadd-subset", required=True, default="")
    parser.add_argument("--template-type", default="")
    parser.add_argument("--where")
    parser.add_argument("--collections", nargs="+", default=[])
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--slurm", action="store_true")
    parser.add_argument("--pipeline-slurm", action="store_true")
    parser.add_argument("--provider", default="EpycProvider")
    parser.add_argument("--workers", "-J", type=int, default=4)
    
    args = parser.parse_args()

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
        run_dir=os.path.join("runinfo", "diff"),
    )
    parsl.load(config)

    butler = dafButler.Butler(args.repo)
    collections = butler.registry.queryCollections(
        re.compile("DEEP/[0-9]{8}/drp"), 
        collectionTypes=CollectionType.CHAINED
    )
    subsets = list(filter(lambda x : re.compile(args.subset).match(x) is not None, map(lambda x : x.split("/")[1], collections)))

    futures = [] # chage to dictionary

    for subset in subsets:
        inputs = []
        cmd = [
            "python",
            "bin/collection.py",
            args.repo,
            "diff_drp",
            subset,
        ]
        if args.template_type:
            cmd += ["--template-type", args.template_type]
        if args.coadd_subset:
            cmd += ["--coadd-subset", args.coadd_subset]

        cmd = " ".join(map(str, cmd))
        func = partial(run_command)
        setattr(func, "__name__", f"collection_{subset}")
        future = bash_app(func)(cmd, inputs=inputs)
        inputs = [future]
        futures.append(future)

        cmd = [
            "python",
            "bin/pipeline.py",
            args.repo,
            "diff_drp",
            subset,
            "--steps", "step4a"
        ]
        if args.template_type:
            cmd += ["--template-type", args.template_type]
        if args.coadd_subset:
            cmd += ["--coadd-subset", args.coadd_subset]
        if args.where:
            cmd += [f"--where \"{args.where}\""]

        cmd = " ".join(map(str, cmd))
        func = partial(run_command)
        setattr(func, "__name__", f"pipeline_diff_{subset}")
        future = bash_app(func)(cmd, inputs=inputs)
        inputs = [future]
        futures.append(future)


        cmd = [
            "python",
            "bin/collection.py",
            args.repo,
            "diff_drp",
            subset,
        ]
        if args.template_type:
            cmd += ["--template-type", args.template_type]
        if args.coadd_subset:
            cmd += ["--coadd-subset", args.coadd_subset]

        cmd = " ".join(map(str, cmd))
        func = partial(run_command)
        setattr(func, "__name__", f"collection_{subset}")
        future = bash_app(func)(cmd, inputs=inputs)
        inputs = [future]
        futures.append(future)

    for future in futures:
        if future:
            future.exception()
    
    parsl.dfk().cleanup()


if __name__ == "__main__":
    main()
