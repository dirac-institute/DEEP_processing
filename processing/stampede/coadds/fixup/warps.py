import argparse
import astropy.table
import atexit, sys, selectors
from subprocess import Popen, PIPE

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
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("input")
    parser.add_argument("output_collection")
    parser.add_argument("--collections")

    args = parser.parse_args()

    t = astropy.table.Table.read(args.input)
    for g in t.group_by(["patch", "band"]).groups:
        patch = g[0]['patch']
        band = g[0]['band']
        visits = ",".join(map(str, g['visit']))
        cmd = [
            "python",
            "bin/warps.py",
            args.repo,
            "allSky/fixup",
            "--collections", args.collections,
            "--where", f"instrument='DECam' and skymap='discrete' and patch={patch} and band='{band}' and visit not in ({visits})",
        ]
        run_and_pipe(cmd)


if __name__ == "__main__":
    main()
