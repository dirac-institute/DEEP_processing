import re
import argparse
import sys
import lsst.daf.butler as dafButler
import astropy.table
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("--collections", nargs="+", default=["*"])
    parser.add_argument("--output", default=sys.stdout)
    parser.add_argument("--format", default="ascii.fast_csv")
    parser.add_argument("--datasetType", default="deepCoadd_directWarp")

    args = parser.parse_args()

    butler = dafButler.Butler(args.repo, writeable=True)

    collections = butler.registry.queryCollections(args.collections)

    refs = list(set(list(butler.registry.queryDatasets(args.datasetType, collections=collections))))
    patches = {}
    for ref in refs:
        patches[ref.dataId['patch']] = patches.get(ref.dataId['patch'], 0) + 1
    
    # grouped_by_count = {}
    # for k, v in patches.items():
    #     grouped_by_count[v] = grouped_by_count.get(v, [])
    #     grouped_by_count[v].append(k)

    outputs = []
    for k, v in patches.items():
        outputs.append(
            {
                "patch": k,
                "n": v,
            }
        )

    outputs = astropy.table.Table(outputs)
    if args.output != sys.stdout and args != sys.stderr:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    outputs.write(args.output, format=args.format)

if __name__ == "__main__":
    main()
