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
    parser.add_argument("--coadd-type", default="deepCoadd")

    args = parser.parse_args()

    butler = dafButler.Butler(args.repo, writeable=True)

    collections = butler.registry.queryCollections(args.collections)
    
    # loop through refs of directWarp and psfMatchedWarp
    # group by patch and band
    # exclude patch/band combinations where n(directWarp) != n(psfMatchedWarp)
    # print (patch, band, n)

    direct_dataset = f"{args.coadd_type}_directWarp"
    direct_refs = set(list(butler.registry.queryDatasets(direct_dataset, collections=collections)))
    psfMatched_dataset = f"{args.coadd_type}_psfMatchedWarp"
    psfMatched_refs = set(list(butler.registry.queryDatasets(psfMatched_dataset, collections=collections)))

    def count_refs(refs, keys=['patch', 'band']):
        counts = {}
        for ref in refs:
            k = (ref.dataId['patch'], ref.dataId['band'])
            counts[k] = counts.get(k, 0) + 1
        return counts

    direct_patches = count_refs(direct_refs)
    psfMatched_patches = count_refs(psfMatched_refs)

    patches = set(list(direct_patches.keys())).intersection(set(list(psfMatched_patches.keys())))

    outputs = []
    for k in patches:
        patch, band = k
        n_direct = direct_patches[k]
        n_psfMatched = psfMatched_patches[k]
        if n_direct != n_psfMatched:
            print("number of direct and psfMatched refs do not match for patch, band", patch, band, file=sys.stderr)
            continue
        outputs.append(
            {
                "patch": patch,
                "band": band,
                "n": n_direct,
            }
        )

    outputs = astropy.table.Table(outputs)
    if args.output != sys.stdout and args.output != sys.stderr:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    outputs.write(args.output, format=args.format)

if __name__ == "__main__":
    main()
