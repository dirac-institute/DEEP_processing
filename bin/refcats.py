"""
Get trimmed refcats for the survey
"""

import atexit
from subprocess import Popen, PIPE
import selectors
import sys

processes = []

def cleanup():
    for p in processes:
        p.kill()

atexit.register(cleanup)

def popen(*args, **kwargs):
    global processes
    p = Popen(*args, **kwargs)
    print("popen: " + " ".join(p.args), file=sys.stderr)
    processes.append(p)
    return p

def _print(p):
    sel = selectors.DefaultSelector()
    if p.stdout is PIPE:
        sel.register(p.stdout, selectors.EVENT_READ)
    
    if p.stderr is PIPE:
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
    import astropy.table
    import os
    from subprocess import Popen

    parser = argparse.ArgumentParser()
    parser.add_argument("exposures")
    parser.add_argument("--refcats", default="/epyc/data/lsst_refcats")

    args = parser.parse_args()

    exposures = astropy.table.Table.read(args.exposures)
    downloaded = astropy.table.Table.read(os.path.join(os.path.dirname(args.exposures), "downloaded_" + os.path.basename(args.exposures)))
    exposures = astropy.table.join(exposures, downloaded, keys=["md5sum"])
    exposures = exposures[
        (
        exposures['obs_type'] == "object"
        )
        & (
            exposures['valid_on_disk']
        )
        & (
            exposures['proc_type'] == "raw"
        )
    ]
    paths = exposures['path']
    
    cmd = [
        os.path.join(args.refcats, "bin", "trim.sh"),
        "ps1",
        "--import-file",
        "-J", "24",
        "--paths",
    ] + list(map(str, paths))
    with open("data/refcats_ps1.ecsv", "w") as o, open("data/refcats_ps1.err", "w") as e:
        ps1 = popen(cmd, stdout=o, stderr=e)
    
    cmd = [
        os.path.join(args.refcats, "bin", "trim.sh"),
        "gaia_dr3",
        "--import-file",
        "-J", "24",
        "--paths",
    ] + list(map(str, paths))
    with open("data/refcats_gaia_dr3.ecsv", "w") as o, open("data/refcats_gaia_dr3.err", "w") as e:
        gaia_dr3 = popen(cmd, stdout=o, stderr=e)
    
    cmd = [
        os.path.join(args.refcats, "bin", "trim.sh"),
        "gaia_dr2",
        "--import-file",
        "-J", "24",
        "--paths",
    ] + list(map(str, paths))
    with open("data/refcats_gaia_dr2.ecsv", "w") as o, open("data/refcats_gaia_dr2.err", "w") as e:
        gaia_dr2 = popen(cmd, stdout=o, stderr=e)
    
    ps1.wait()
    gaia_dr3.wait()
    gaia_dr2.wait()

if __name__ == "__main__":
    main()
