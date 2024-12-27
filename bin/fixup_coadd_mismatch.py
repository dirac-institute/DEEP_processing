import argparse
import re
import astropy.table
import sys
from pathlib import Path
import logging
import lsst.daf.butler as dafButler
from lsst.daf.butler.registry import CollectionType

logging.basicConfig()
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=str)
    parser.add_argument("output_collection", type=str)
    parser.add_argument("--input", type=Path, nargs="+")
    parser.add_argument("--output", default=sys.stdout)
    parser.add_argument("--format", default="ascii.fast_csv")
    parser.add_argument("--collections", type=str, default="DEEP/allSky/coadd/warps")
    parser.add_argument("--coadd-type", type=str, default="deepCoadd")
    parser.add_argument("--log-level", default="INFO")

    args = parser.parse_args()

    logging.getLogger().setLevel(args.log_level)

    i = re.compile("INFO.*Weight of (.*) \{.*patch: (\d+),.*visit: (\d+),.*band: '(\w+)',.*\}.*")
    e = re.compile("WARNING.*(deepCoadd_.*Warp)_.*with data ID \{.*patch: (\d+),.*visit: (\d+),.*band: '(\w+)',.*\}.*")

    d = {
        "included": {},
        "excluded": {},
    }
    for i in args.input:
        with open(i, "r") as f:
            while line := f.readline():
                m = i.match(line)
                if m:
                    c, p, v, b = m.groups()
                    d['included'][c] = d['included'].get(c, [])
                    d['included'][c].append((p, v, b))
                    
                m = e.match(line)
                if m:
                    c, p, v, b = m.groups()
                    d['excluded'][c] = d['excluded'].get(c, [])
                    d['excluded'][c].append((p, v, b))
    
    diff = set()
    for c in d['excluded']:
        diff = diff.symmetric_difference(set(d['excluded'][c]))
    
    o = []
    for p, v, b in diff:
        o.append(
            {
                "patch": int(p),
                "visit": int(v), 
                "band": b,
            }
        )
    o = astropy.table.Table(o)
    o.sort(["patch", "visit"])

    butler = dafButler.Butler(args.repo, writeable=True)

    collections = butler.registry.queryCollections(args.collections)
    logger.info("registering %s", args.output_collection)
    butler.registry.registerCollection(args.output_collection, CollectionType.TAGGED)

    for g in o.group_by(["patch", "band"]).groups:
        patch = g[0]['patch']
        band = g[0]['band']
        visits = ",".join(map(str, g['visit']))
        for dataset in [f"{args.coadd_type}_directWarp", f"{args.coadd_type}_psfMatchedWarp"]:
            refs = butler.registry.queryDatasets(
                dataset, 
                where=f"instrument='DECam' and skymap='discrete' and patch={patch} and band='{band}' and visit not in ({visits})", 
                collections=collections
            )
            refs = list(set(list(refs)))
            refs_c = butler.registry.queryDatasets(
                dataset, 
                where=f"instrument='DECam' and skymap='discrete' and patch={patch} and band='{band}'", 
                collections=collections
            )
            refs_c = list(set(list(refs_c)))

            for ref in refs:
                assert(ref.dataId['visit'] not in g['visit'])

            logger.info(
                "associatating %s/%s of %s into %s", 
                len(refs), 
                len(set(refs).union(set(refs_c))),
                dataset, 
                args.output_collection
            )
            butler.registry.associate(args.output_collection, refs)            

    if args.output != sys.stdout and args != sys.stderr:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    o.write(args.output, format=args.format)

if __name__ == "__main__":
    main()
