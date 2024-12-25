import lsst.daf.butler as dafButler
from pathlib import Path
import astropy.table
import logging
from lsst.daf.butler.registry import CollectionType, MissingCollectionError

logging.basicConfig()
logger = logging.getLogger(__name__)

def dimensions(refs):
    d = {}
    for ref in refs:
        patch, visit, band = ref.dataId['patch'], ref.dataId['visit'], ref.dataId['band']
        d[patch] = d.get(patch, {})
        d[patch][band] = d[patch].get(band, {})
        n = d[patch][band].get(visit, 0)
        if n == 0:
            d[patch][band][visit] = ref
        
    return d

def common(d1, d2, t):
    return list(set(getattr(d1, t)()).intersection(set(getattr(d2, t)())))

def get_warps(butler, collections, coadd_type):
    direct_refs = butler.registry.queryDatasets(
        f"{coadd_type}_directWarp",
        where="instrument='DECam' and skymap='discrete'",
        collections=collections,
    )
    psfMatched_refs = butler.registry.queryDatasets(
        f"{coadd_type}_psfMatchedWarp",
        where="instrument='DECam' and skymap='discrete'",
        collections=collections,
    )
    
    direct_dimensions = dimensions(direct_refs)
    psfMatched_dimensions = dimensions(psfMatched_refs)
    
    warps = []
    warp_counts = []

    common_patches = common(direct_dimensions, psfMatched_dimensions, "keys")
    for patch in common_patches:
        direct_bands = direct_dimensions[patch]
        psfMatched_bands = psfMatched_dimensions[patch]
        common_bands = common(direct_bands, psfMatched_bands, "keys")
        for band in common_bands:
            direct_visits = direct_dimensions[patch][band]
            psfMatched_visits = psfMatched_dimensions[patch][band]
            n_direct = len(direct_visits)
            n_psfMatched = len(psfMatched_visits)
            if n_direct != n_psfMatched:
                logger.warning(f"number of visits mismatch in patch={patch} band={band} direct={n_direct} psfMatched={n_psfMatched}")

            common_visits = common(direct_visits, psfMatched_visits, "keys")
            warp_counts.append(
                {
                    "patch": patch,
                    "band": band,
                    "n": len(common_visits),
                }
            )
            for visit in common_visits:
                warps.append(
                    {
                        "patch": patch,
                        "band": band,
                        "visit": visit,
                    }
                )

    warps = astropy.table.Table(warps)
    warp_counts = astropy.table.Table(warp_counts)
    return warps, warp_counts, direct_dimensions, psfMatched_dimensions

def make_subsets(t, n_max):
    t.sort("n")
    subsets = [[]]
    c = 0
    for r in t:
        c += r['n']
        if c > int(n_max):
            subsets[-1] = astropy.table.vstack(subsets[-1])
            subsets.append([r])
            c = r['n']
        else:
            subsets[-1].append(r)

    subsets[-1] = astropy.table.vstack(subsets[-1])
    return subsets

def get_refs(subset, warps, direct_refs, psfMatched_refs):
    refs = []
    for r in subset:
        patch, band = r['patch'], r['band']
        m = (warps['patch'] == patch) & (warps['band'] == band)
        visits = warps['visit'][m]
        refs.extend([direct_refs[patch][band][visit] for visit in visits])
        refs.extend([psfMatched_refs[patch][band][visit] for visit in visits])
    return refs

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=str)
    parser.add_argument("prefix", type=str)
    parser.add_argument("--collections", nargs="+", default=["*"])
    # parser.add_argument("--output", default=sys.stdout)
    # parser.add_argument("--format", default="ascii.fast_csv")
    parser.add_argument("--coadd-type", default="deepCoadd")
    parser.add_argument("--group", action="store_true")
    parser.add_argument("--max-warps", type=int, default=int(1e4))
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--no-associate", action="store_true")

    args = parser.parse_args()

    args.output_dir.mkdir(exist_ok=True, parents=True)

    logging.getLogger().setLevel(args.log_level)

    butler = dafButler.Butler(args.repo, writeable=True)

    collections = butler.registry.queryCollections(args.collections)
    warps, warp_counts, direct_refs, psfMatched_refs = get_warps(butler, collections, args.coadd_type)

    p = args.output_dir / "warps.csv"
    logger.info("writing to %s", p)
    warps.write(p)
    p = args.output_dir / "warp_counts.csv"
    logger.info("writing to %s", p)
    warp_counts.write(p)

    subsets = []
    if args.group:
        for g in warp_counts.group_by("n").groups:
            subsets.extend(make_subsets(g, args.max_warps))
    else:
        subsets.extend(make_subsets(warp_counts, args.max_warps))
    
    (args.output_dir / "subsets").mkdir(exist_ok=True, parents=True)
    for i, subset in enumerate(subsets):
        p = args.output_dir / "subsets" / f"{i}.csv"
        logger.info("writing to %s", p)
        subset.write(p)
        if not args.no_associate:
            shard = get_refs(subset, warps, direct_refs, psfMatched_refs)
            tagged = f"{args.prefix}/{i}"
            try:
                logger.info("removing collection %s", tagged)
                butler.registry.removeCollection(tagged)
            except MissingCollectionError:
                pass
            logger.info("creating collection %s", tagged)
            butler.registry.registerCollection(tagged, CollectionType.TAGGED)
            logger.info("associatating %s warps into %s", len(shard), tagged)
            butler.registry.associate(tagged, shard)


if __name__ == "__main__":
    main()
