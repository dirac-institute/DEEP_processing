import re
import argparse
import sys
import lsst.daf.butler as dafButler
import astropy.table
from pathlib import Path

def parse_coadd_log(log):
    regex = re.compile(".*Assembling (\d+) (.*)")
    d = {}
    for record in log:
        m = regex.match(record.message)
        if m:
            num_warps = m.groups()[0]
            warp_type = m.groups()[1]
            d[warp_type] = num_warps
    return d

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("--collections", nargs="+", default=["*"])
    parser.add_argument("--output", default=sys.stdout)
    parser.add_argument("--format", default="ascii.fast_csv")
    
    args = parser.parse_args()

    butler = dafButler.Butler(args.repo, writeable=True)

    collections = butler.registry.queryCollections(args.collections)
    # look for assembleCoadd_log
    refs = list(butler.registry.queryDatasets("assembleCoadd_log", collections=collections))
    print("found", len(refs), "coadd logs", file=sys.stderr)

    inputs = []
    for ref in refs:
        log = butler.get(ref)
        d = {}
        for k, v in ref.dataId.mapping.items():
            d[k] = v
        d['run'] = ref.run
        d.update(parse_coadd_log(log))
        inputs.append(d)

    inputs = astropy.table.Table(inputs)
    if args.output != sys.stdout and args != sys.stderr:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    inputs.write(args.output, format=args.format)

if __name__ == "__main__":
    main()
