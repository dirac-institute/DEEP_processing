import re
import argparse
import sys
import lsst.daf.butler as dafButler
import astropy.table
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("datasets")
    parser.add_argument("--collections", nargs="+", default=["*"])
    parser.add_argument("--output", default=sys.stdout)
    parser.add_argument("--format", default="ascii.fast_csv")
    parser.add_argument("--agg", action="store_true")
    
    args = parser.parse_args()

    butler = dafButler.Butler(args.repo, writeable=True)

    collections = butler.registry.queryCollections(args.collections)
    refs = list(butler.registry.queryDatasets(args.datasets, collections=collections))

    sizes = []
    for ref in refs:
        size = butler.getURI(ref).size()
        d = {}
        for k, v in ref.dataId.mapping.items():
            d[k] = v
        d['run'] = ref.run
        d['name'] = ref.datasetType.name
        d.update({"size": size})
        sizes.append(d)

    sizes = astropy.table.Table(sizes)
    t = sizes

    if args.agg:
        agg = []
        for g in sizes.group_by("name").groups:
            agg.append(
                {
                    "name": g[0]['name'],
                    "size": g['size'].sum(),
                    "datasets": len(g),
                }
            )
        agg = astropy.table.Table(agg)
        t = agg

    if args.output != sys.stdout and args != sys.stderr:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    t.write(args.output, format=args.format)

if __name__ == "__main__":
    main()
