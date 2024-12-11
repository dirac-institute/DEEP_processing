"""
Get the fakes for a given night
"""

def main():
    import argparse
    import astropy.table
    import lsst.daf.butler as dafButler
    from lsst.source.injection import ingest_injection_catalog

    import numpy as np

    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("fakes")
    parser.add_argument("--collection", default="DEEP/fakes")

    args = parser.parse_args()

    fakes = astropy.table.Table.read(args.fakes)

    def rename_if_not_exist(x, y, default=None):
        if y not in fakes.columns:
            if x in fakes.columns:
                fakes.rename_columns([x], [y])
            elif default is not None:
                fakes[y] = default

    rename_if_not_exist("RA", "ra")
    rename_if_not_exist("DEC", "dec")
    rename_if_not_exist("MAG", "mag")
    rename_if_not_exist("BAND", "band", default="VR")

    if 'source_type' not in fakes.columns:
        fakes['source_type'] = "DeltaFunction"

    butler = dafButler.Butler(args.repo, writeable=True)
    for group in fakes.group_by("band").groups:
        band = group[0]['band']
        if band == "Y": # alias doesn't work for some reason https://github.com/lsst/obs_decam/blob/main/python/lsst/obs/decam/decamFilters.py#L39
            band = 'y'
        refs = ingest_injection_catalog(
            writeable_butler=butler,
            table=group,
            band=band,
            output_collection=args.collection,
        )
        print("ingested", len(group), f"{band}-band fakes into", len(refs), "datasets")

if __name__ == "__main__":
    main()
