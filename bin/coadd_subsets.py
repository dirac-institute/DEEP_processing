"""
Aggregate over available input warps to make a coadd

This should select input warps with the where query and collections
Associate those into DEEP/{coadd_name}/warps
Make a new chained collection DEEP/{coadd_name} and execute.py on the input
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

def delay():
    import time
    import random
    time.sleep(random.randint(1, 5) + random.randint(0, 10)/10)

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
    # loop over subsets?
    import argparse
    import os
    from pathlib import Path
    import re

    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("coadd_name")
    parser.add_argument("warp_subset_dir", type=Path)
    parser.add_argument("--steps", nargs="+", default=["assembleCoadd"])
    parser.add_argument("--subsets", default=".*")
    parser.add_argument("--template-type", default="")
    parser.add_argument("--where")
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
        run_dir=os.path.join("runinfo", "coadd"),
    )
    parsl.load(config)

    subsets = list(
        filter(
            lambda x : re.compile(args.subsets).match(x) is not None, 
            map(
                lambda x : x.name.strip(".csv"), 
                args.warp_subset_dir.rglob("*.csv")
            )
        )
    )
    
    futures = [] # change to dictionary
    for subset in subsets:
        inputs = []
        cmd = [
            "python",
            "bin/collection.py",
            args.repo,
            "coadd",
            args.coadd_name,
            "--coadd-subset", subset
        ]
        if args.template_type:
            cmd += ["--template-type", args.template_type]

        cmd = " ".join(map(str, cmd))
        func = partial(run_command)
        setattr(func, "__name__", f"collection_{subset}")
        future = bash_app(func)(cmd, inputs=inputs)
        inputs = [future]
        futures.append(future)
            
        delay()

        cmd = [
            "python",
            "bin/pipeline.py",
            args.repo,
            "coadd",
            args.coadd_name,
            "--coadd-subset", subset,
            "--steps"
        ] + args.steps
        if args.pipeline_slurm:
            cmd += ["--slurm"]
        if args.where:
            cmd += [f"--where \"{args.where}\""]

        cmd = " ".join(map(str, cmd))
        func = partial(run_command)
        setattr(func, "__name__", f"execute_coadd_subset_{subset}")
        future = bash_app(func)(cmd, inputs=inputs)
        inputs = [future]
        futures.append(future)

        delay()

        cmd = [
            "python",
            "bin/collection.py",
            args.repo,
            "coadd",
            args.coadd_name,
            "--coadd-subset", subset
        ]
        if args.template_type:
            cmd += ["--template-type", args.template_type]

        cmd = " ".join(map(str, cmd))
        func = partial(run_command)
        setattr(func, "__name__", f"collection_{subset}")
        future = bash_app(func)(cmd, inputs=inputs)
        inputs = [future]
        futures.append(future)

        delay()

    for future in futures:
        if future:
            future.exception()
    
    parsl.dfk().cleanup()


if __name__ == "__main__":
    main()
