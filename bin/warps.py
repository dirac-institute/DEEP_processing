import os
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)

def main():
    """
    
    """
    import argparse
    import lsst.daf.butler as dafButler
    from lsst.daf.butler.registry import CollectionType, MissingCollectionError

    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("subset")
    parser.add_argument("--collections", nargs="+", default=[])
    parser.add_argument("--where")
    parser.add_argument("--log-level", default="INFO")

    args = parser.parse_args()
    
    logging.getLogger().setLevel(args.log_level)

    butler = dafButler.Butler(args.repo, writeable=True)

    tagged = os.path.normpath(f"DEEP/{args.subset}/coadd/warps")
    
    if args.collections:
        collections = butler.registry.queryCollections(args.collections)
    else:
        collections = "*"

    butler.registry.registerCollection(tagged, CollectionType.TAGGED)
    for warp_type in ["psfMatched", "direct"]:
        dataset = f"deepCoadd_{warp_type}Warp"
        warps = list(set(list(butler.registry.queryDatasets(
            dataset,
            collections=collections,
            where=args.where,
            findFirst=True,
        ))))

        logger.info("associatating %s of %s into %s", len(warps), dataset, tagged)
        butler.registry.associate(tagged, warps)

if __name__ == "__main__":
    main()
