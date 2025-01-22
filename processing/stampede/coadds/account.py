def main():
    import argparse
    import lsst.daf.butler as dafButler
    import re

    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("--collections", required=True)
    parser.add_argument("--where", default=None)

    args = parser.parse_args()

    butler = dafButler.Butler(args.repo)

    collections = butler.registry.queryCollections(args.collections)
    coadds = butler.registry.queryDatasets(
        "deepCoadd",
        collections=collections,
        where=args.where,
        findFirst=True,
    )
    logs = butler.registry.queryDatasets(
        "assembleCoadd_log",
        collections=collections,
        where=args.where,
        findFirst=True,
    )
    metadata = butler.registry.queryDatasets(
        "assembleCoadd_metadata",
        collections=collections,
        where=args.where,
        findFirst=True,
    )
    coadds = list(set(list(coadds)))
    logs = list(set(list(logs)))
    metadata = list(set(list(metadata)))
    
    def make_count(refs):
        d = {}
        for ref in refs:
            k = ref.dataId['tract'], ref.dataId['patch'], ref.dataId['band']
            d[k] = d.get(k, [])
            d[k].append(ref)
            # if d.get(k, -1) == -1:
            #     d[k] = ref
        return d

    print("there are", len(coadds), "deepCoadd")
    print("there are", len(logs), "assembleCoadd_log")
    print("there are", len(metadata), "assembleCoadd_metadata")

    coadds_d = make_count(coadds)
    logs_d = make_count(logs)
    metadata_d = make_count(metadata)

    print("there are", len(coadds_d), "deepCoadd (tract, patch, band)")
    print("there are", len(logs_d), "assembleCoadd_log (tract, patch, band)")
    print("there are", len(metadata_d), "assembleCoadd_metadata (tract, patch, band)")

    for k in coadds_d:
        refs = coadds_d[k]
        if len(refs) > 1:
            print("duplicate deepCoadd:", k)
            break

    failures = sorted(set(list(logs_d.keys())).difference(set(list(metadata_d.keys()))), key=lambda x : x[0])
    print("failures:", failures)

    error_pattern = re.compile(".*failed. Exception ([a-zA-Z]+):(.*)")
    errors = {}
    for k in failures:
        error = []
        for ref in logs_d[k]:
            log = butler.get(ref)
            for record in log:
                m = error_pattern.match(record.message)
                if m:
                    error.extend(m.groups())
                    # errors[k] = " ".join()
                    break
        if len(error) > 0:
            errors[k] = " ".join(list(set(error)))
    
    reasons = set(list(errors.values()))
    print("failure reasons:", reasons)

    missing = sorted(set(list(metadata_d.keys())).difference(set(list(coadds_d.keys()))), key=lambda x : x[0])
    no_data_pattern = re.compile(".*Found 0 deepCoadd_directWarp.*|.*Found 0 deepCoadd_psfMatchedWarp.*")
    no_data_k = {}
    for k in missing:
        for ref in logs_d[k]:
            log = butler.get(ref)
            for record in log:
                m = no_data_pattern.match(record.message)
                if m:
                    no_data_k[k] = 1
                    break

    print(len(no_data_k), "of", len(missing), "missing are no data")

if __name__ == "__main__":
    main()
