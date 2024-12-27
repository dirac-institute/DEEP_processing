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
    parser.add_argument("output_collection", type=str)
    parser.add_argument("--patch", type=int, required=True)
    parser.add_argument("--band", type=str, required=True)
    parser.add_argument("--collections", type=str, default="DEEP/allSky/coadd/warps")
    parser.add_argument("--coadd-type", type=str, default="deepCoadd")
    parser.add_argument("--log-level", default="INFO")

    args = parser.parse_args()
    
    logging.getLogger().setLevel(args.log_level)

    butler = dafButler.Butler(args.repo, writeable=True)

    collections = butler.registry.queryCollections(args.collections)
    logger.info("registering %s", args.output_collection)
    butler.registry.registerCollection(args.output_collection, CollectionType.TAGGED)
    for dataset in [f"{args.coadd_type}_directWarp", f"{args.coadd_type}_psfMatchedWarp"]:
        
        refs = butler.registry.queryDatasets(
            dataset, 
            where=f"instrument='DECam' and skymap='discrete' and patch={args.patch} and band='{args.band}' and detector=31", 
            collections=collections
        )
        refs = list(set(list(refs)))

        refs_c = butler.registry.queryDatasets(
            dataset, 
            where=f"instrument='DECam' and skymap='discrete' and patch={args.patch} and band='{args.band}' and detector!=31", 
            collections=collections
        )
        refs_c = list(set(list(refs_c)))
        fixed = list(set(refs_c).difference(set(refs)))

        for ref in fixed:
            patch = ref.dataId['patch']
            visit = ref.dataId['visit']
            assert(31 not in list(set(list(map(lambda x : x.id, butler.registry.queryDimensionRecords("detector", where=f"instrument='DECam' and skymap='discrete' and patch={patch} and visit={visit}"))))))        
        
        logger.info("associatating %s/%s of %s into %s", len(fixed), len(set(refs_c).union(set(refs))), dataset, args.output_collection)
        butler.registry.associate(args.output_collection, fixed)

if __name__ == "__main__":
    main()
