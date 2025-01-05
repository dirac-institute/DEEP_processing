import lsst.daf.butler as dafButler
import argparse
from collections import Counter
import astropy.table
from pathlib import Path
import sys
from joblib import Parallel, delayed
from tqdm import tqdm
from lsst.daf.butler.registry import CollectionType

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("--detector", default=31, type=int)
    parser.add_argument("--output", default=sys.stdout)
    parser.add_argument("--format", default="ascii.fast_csv")
    parser.add_argument("--processes", "-J", type=int, default=1)

    args = parser.parse_args()

    butler = dafButler.Butler(args.repo)

    # patches = butler.registry.queryDimensionRecords("patch", where="instrument='DECam' and skymap='discrete' and detector=31")
    patches = butler.registry.queryDimensionRecords("patch", datasets="deepCoadd", collections=butler.registry.queryCollections("DEEP/allSky/*/coadd", collectionTypes=CollectionType.CHAINED))
    # p = iter(butler.registry.queryDimensionRecords("patch", where="instrument='DECam' and skymap='discrete' and detector=31"))
    # patches = [next(iter(butler.registry.queryDimensionRecords("patch", where="instrument='DECam' and skymap='discrete' and detector=31")))]
    # patches = [next(p), next(p)]
    # patches = [next(iter(patches))]
    # print(patches)

    def inner(patch_id):
        detectors = butler.registry.queryDimensionRecords("visit_detector_region", where=f"instrument='DECam' and skymap='discrete' and patch={patch_id}")
        c = Counter(list(map(lambda x : x.detector, detectors)))
        return patch_id, c[args.detector]/sum(c.values())

    ratios = {}
    for patch_id, ratio in Parallel(n_jobs=args.processes)(delayed(inner)(patch.id) for patch in tqdm(patches)):
        if ratios.get(patch_id, -1) == -1:
            ratios[patch_id] = ratio

    ratios = [{"patch": p, "ratio": r} for p, r in ratios.items()]
    ratios = astropy.table.Table(ratios)
    if args.output != sys.stdout and args != sys.stderr:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    ratios.write(args.output, format=args.format)


if __name__ == "__main__":
    main()
