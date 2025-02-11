import logging

logging.basicConfig()
logger = logging.getLogger(__name__)

inputs = dict(
    bias=[
        "DECam/calib",
        "DEEP/{subset}/bias/raw",
    ],
    flat=[
        "DEEP/{subset}/calib/bias",
        "DECam/calib",
        "DEEP/{subset}/flat/raw",
    ],
    science=[
        "DEEP/fakes",
        "refcats",
        "skymaps",
        "DEEP/{subset}/calib/flat",
        "DEEP/{subset}/calib/bias",
        "DEEP/calib",
        "DECam/calib",
        "DEEP/{subset}/science/raw",
    ],
    drp=[
        "DEEP/fakes",
        # "DEEP/fakes/template_tests_dense", # temporary for 20190829
        # "DEEP/fakes/extra", # temporary for 20190401
        "refcats",
        "skymaps",
        "DEEP/{subset}/calib/flat",
        "DEEP/{subset}/calib/bias",
        "DEEP/calib",
        "DECam/calib",
        "DEEP/{subset}/drp/raw",
    ],
    coadd=[
        "DEEP/{subset}/{coadd_subset}/coadd/warps",
        "skymaps",
    ],
    diff_drp=[
        "DEEP/{coadd_subset}/{template_type}/coadd", # coadds
        "DEEP/{subset}/drp", # calexp
    ]
)

def main():
    """
    
    """
    import argparse
    import lsst.daf.butler as dafButler
    from lsst.daf.butler.registry import CollectionType, MissingCollectionError
    from datetime import datetime
    import os
    import re

    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("proc_type")
    parser.add_argument("subset")
    parser.add_argument("--coadd-subset", default="")
    parser.add_argument("--template-type", default="")
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--overwrite", action="store_true")

    args = parser.parse_args()
    
    logging.getLogger().setLevel(args.log_level)

    butler = dafButler.Butler(args.repo, writeable=True)

    parent = os.path.normpath(f"DEEP/{args.subset}/{args.coadd_subset}/{args.template_type}/{args.proc_type}")
    
    input_collections = list(map(lambda x : os.path.normpath(x.format(subset=args.subset, template_type=args.template_type, coadd_subset=args.coadd_subset)), inputs[args.proc_type]))
    input_runs = butler.registry.queryCollections(parent + "/*", collectionTypes=CollectionType.RUN)
    
    date_runs = []
    non_date_runs = []
    for run in input_runs:
        if re.compile("\d{8}T\d{6}Z").match(run.split("/")[-1]) is not None:
            date_runs.append(run)
        else:
            non_date_runs.append(run)
    input_runs = sorted(date_runs, key=lambda x : datetime.fromisoformat(x.split("/")[-1]), reverse=True) + sorted(non_date_runs)

    chain = []
    for child in input_runs + input_collections:
        try:
            butler.registry.queryCollections(child)
            chain.append(child)
        except MissingCollectionError:
            logger.warning("%s missing child %s", parent, child)
            pass

    logger.info("setting %s to chain %s", parent, chain)
    try:
        existing = butler.registry.getCollectionChain(parent)
        missing = set(existing).difference(set(chain))
        new = set(chain).difference(set(existing))
        if missing:
            logger.warning("missing children %s", missing)
            if args.overwrite:
                butler.registry.setCollectionChain(parent, chain)
        else:
            if new:
                logger.info("adding new children %s", new)
            butler.registry.setCollectionChain(parent, chain)
    except MissingCollectionError:
        butler.registry.registerCollection(parent, CollectionType.CHAINED)
        butler.registry.setCollectionChain(parent, chain)

if __name__ == "__main__":
    main()
