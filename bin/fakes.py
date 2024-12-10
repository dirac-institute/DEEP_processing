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

    if 'RA' in fakes.columns:
        fakes['ra'] = fakes['RA']
    if 'DEC' in fakes.columns:
        fakes['dec'] = fakes['DEC']
    if 'MAG' in fakes.columns:
        fakes['mag'] = fakes['MAG']
    if 'source_type' not in fakes.columns:
        fakes['source_type'] = "DeltaFunction"
    if 'BAND' in fakes.columns:
        fakes['band'] = fakes['BAND']

    butler = dafButler.Butler(args.repo, writeable=True)
    
    if "band" in fakes.columns:
        for group in fakes.group_by("band").groups:
            refs = ingest_injection_catalog(
                writeable_butler=butler,
                table=group,
                band=group[0]['band'],
                output_collection=args.collection,
            )
            print("ingested", len(group), "fakes into", len(refs), "datasets")
    else:
        refs = ingest_injection_catalog(
            writeable_butler=butler,
            table=fakes,
            band="VR",
            output_collection=args.collection,
        )
        print("ingested", len(fakes), "fakes into", len(refs), "datasets")

if __name__ == "__main__":
    main()
