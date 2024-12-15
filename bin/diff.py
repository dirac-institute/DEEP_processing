"""
"""
import parsl
from parsl import bash_app
from parsl.executors import HighThroughputExecutor
from functools import partial
from deep.parsl import run_command
from deep.parsl import EpycProvider, KloneAstroProvider, run_command
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

    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("subset")
    parser.add_argument("--template-type", default="")
    parser.add_argument("--coadd-subset", default="")
    parser.add_argument("--where")
    parser.add_argument("--collections", nargs="+", default=[])
    
    args = parser.parse_args()

    # for dataset_type in ["deepCoadd_directWarp", "deepCoadd_psfMatchedWarp"]:
    #     cmd = [
    #         "butler",
    #         "associate",
    #         args.repo,
    #         f"DEEP/{args.subset}/coadd/warps",
    #         "--dataset-type", dataset_type,
    #     ]
    #     if args.collections:
    #         cmd += ["--collections", args.collections]
    #     if args.where:
    #         cmd += [f"--where '{args.where}'"]
    #     cmd = " ".join(map(str, cmd))
    #     print(cmd)

    # cmd = [
    #     "python",
    #     "bin/warps.py",
    #     args.repo,
    #     os.path.normpath(f"{args.subset}/{args.coadd_subset}"),
    # ]
    # if args.collections:
    #     cmd += ["--collections"] + args.collections
    # if args.where:
    #     cmd += ['--where', args.where]
    # # cmd = " ".join(map(str, cmd))
    # # print(cmd)
    # p = run_and_pipe(cmd)
    # p.wait()
    # if p.returncode != 0:
    #     raise RuntimeError("warps failed")

    cmd = [
        "python",
        "bin/collection.py",
        args.repo,
        "diff_drp",
        args.subset,
    ]
    if args.template_type:
        cmd += ["--template-type", args.template_type]
    if args.coadd_subset:
        cmd += ["--coadd-subset", args.coadd_subset]
    # cmd = " ".join(map(str, cmd))
    # print(cmd)
    p = run_and_pipe(cmd)
    p.wait()
    if p.returncode != 0:
        raise RuntimeError("collection failed")

    cmd = [
        "python",
        "bin/execute.py",
        args.repo,
        os.path.normpath(f"DEEP/{args.subset}/{args.coadd_subset}/{args.template_type}/diff_drp"),
        "--pipeline", f"./pipelines/DEEP-DRP.yaml#step4a",
    ]
    if args.where:
        cmd += [f"--where \"{args.where}\""]
    # cmd = " ".join(map(str, cmd))
    # print(cmd)
    p = run_and_pipe(cmd)
    p.wait()
    if p.returncode != 0:
        raise RuntimeError("execute failed")

    cmd = [
        "python",
        "bin/collection.py",
        args.repo,
        "diff_drp",
        args.subset,
    ]
    if args.template_type:
        cmd += ["--template-type", args.template_type]
    if args.coadd_subset:
        cmd += ["--coadd-subset", args.coadd_subset]
    # cmd = " ".join(map(str, cmd))
    # print(cmd)
    p = run_and_pipe(cmd)
    p.wait()
    if p.returncode != 0:
        raise RuntimeError("collection failed")



if __name__ == "__main__":
    main()
