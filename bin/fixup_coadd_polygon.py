import argparse
import re
import astropy.table
import sys
from pathlib import Path
import lsst.daf.butler as dafButler
from lsst.daf.butler.registry import CollectionType
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=str)
    # parser.add_argument("output_collection", type=str)
    parser.add_argument("--input", type=str, nargs="+", required=True)
    # parser.add_argument("--patch", type=int, required=True)
    # parser.add_argument("--band", type=str, required=True)
    parser.add_argument("--exclude", type=int, nargs="+", default=[31])
    parser.add_argument("--collections", type=str, default="DEEP/allSky/coadd/warps")
    parser.add_argument("--coadd-type", type=str, default="deepCoadd")
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--output", default=sys.stdout)
    parser.add_argument("--format", default="ascii.fast_csv")

    args = parser.parse_args()
    
    logging.getLogger().setLevel(args.log_level)

    butler = dafButler.Butler(args.repo, writeable=True)

    collections = butler.registry.queryCollections(args.collections)
    # logger.info("registering %s", args.output_collection)
    # butler.registry.registerCollection(args.output_collection, CollectionType.TAGGED)
    r = re.compile(".*\{band: '(\w+)',.*patch: (\d+)}.*")
    _exclude = ",".join(map(str, args.exclude))
    o = {}

    for i in args.input:
        # get patch and band
        patch, band = None, None 
        with open(i, "r") as f:
            while line := f.readline():
                m = r.match(line)
                if m:
                    band, patch = m.groups()
                if patch is not None and band is not None:
                    break
        
        for dataset in [f"{args.coadd_type}_directWarp", f"{args.coadd_type}_psfMatchedWarp"]:
            o[dataset] = o.get(dataset, [])
            refs_excluded = butler.registry.queryDatasets(
                dataset, 
                where=f"instrument='DECam' and skymap='discrete' and patch={patch} and band='{band}' and detector in ({_exclude})", 
                collections=collections
            )
            refs_excluded = set(list(refs_excluded))

            refs_included = butler.registry.queryDatasets(
                dataset, 
                where=f"instrument='DECam' and skymap='discrete' and patch={patch} and band='{band}' and detector not in ({_exclude})", 
                collections=collections
            )
            refs_included = set(list(refs_included))
            
            refs = refs_included.union(refs_excluded)
            included = refs_included.difference(refs_excluded)
            excluded = refs.difference(included)            

            if len(included) == 0:
                logger.info("not including any visits for dataset=%s patch=%s band='%s", dataset, patch, band)
                continue
            else:
                # ensure the detector has been excluded
                included_visits = ",".join(map(str, [ref.dataId['visit'] for ref in included]))
                detector_records = list(set(list(map(
                    lambda x : x.id, 
                    butler.registry.queryDimensionRecords("detector", where=f"instrument='DECam' and skymap='discrete' and patch={patch} and visit in ({included_visits})")
                ))))
                assert(
                    all(
                        [
                            detector not in detector_records
                            for detector in args.exclude
                        ]
                    )
                )

            if len(excluded) == 0:
                logger.info("not excluding any visits for dataset=%s patch=%s band='%s", dataset, patch, band)
                continue
            else:
                excluded_visits = ",".join(map(str, [ref.dataId['visit'] for ref in excluded]))
                # ensure we are not excluding refs we don't need to
                detector_records = list(set(list(map(
                    lambda x : x.id, 
                    butler.registry.queryDimensionRecords("detector", where=f"instrument='DECam' and skymap='discrete' and patch={patch} and visit in ({excluded_visits})")
                ))))
                assert(
                    all(
                        [
                            detector in detector_records
                            for detector in args.exclude
                        ]
                    )
                )

            logger.info("excluding %d / %d of %s for patch=%s band='%s", len(excluded), len(refs), dataset, patch, band)
            for ref in excluded:
                o[dataset].append(
                    (patch, band, ref.dataId['visit'])
                )
        
    # ensure same number of the two types of warps
    assert(all([l == len(o[next(iter(o.keys()))]) for l in [len(o[dataset]) for dataset in o]]))

    o = set(o[next(iter(o.keys()))])
    o = [{"patch": p, "band": b, "visit": v} for p, b, v in o]
    o = astropy.table.Table(o)
    if args.output != sys.stdout and args != sys.stderr:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    o.write(args.output, format=args.format)        

if __name__ == "__main__":
    main()
