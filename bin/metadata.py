def main():
    import argparse
    import re
    import sys
    import lsst.daf.butler as dafButler
    import astropy.table
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("--collections")
    parser.add_argument("--tasks", nargs="+", default=['.*'])
    parser.add_argument("--output", nargs="?", default=sys.stdout)
    parser.add_argument("--format", type=str, default='ascii.fast_csv')

    args = parser.parse_args()

    butler = dafButler.Butler(args.repo)
    collections = butler.registry.queryCollections(args.collections)

    refs = []
    for task in args.tasks:
        t = task + "_metadata"
        _refs = list(set(list(butler.registry.queryDatasets(re.compile(t), collections=collections))))
        print("there are", len(_refs), "of", t, "in", collections, file=sys.stderr)
        refs.extend(_refs)

    refs = list(set(refs))
    print("there are", len(refs), "total", file=sys.stderr)

    timing_info = []
    for ref in refs:
        task = ref.datasetType.name.split("_metadata")[0]
        d = {
            "task": task,
            "run": ref.run,
            "id": ref.id,
        }
        for k, v in ref.dataId.mapping.items():
            d[k] = v

        metadata = butler.get(ref)

        for k in metadata['quantum'].keys():
            if k != '__version__':
                d[k] = metadata['quantum'][k]

        timing_info.append(d)
    
    timing_info = astropy.table.Table(timing_info)
    if args.output != sys.stdout and args != sys.stderr:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    timing_info.write(args.output, format=args.format)

if __name__ == "__main__":
    main()