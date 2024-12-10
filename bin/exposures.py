import deep.noirlab.query as noirlab_query
import deep.noirlab.api as noirlab_api
import astropy.table
import astropy.time
import sys
import astropy.units as u
import astropy.coordinates
import os

def survey_exposures(proposal):
    outfields = [ 
        "archive_filename", "obs_type", "proc_type", 
        "prod_type", "md5sum", "dateobs_min", "caldat", 
        "exposure", 
        "RA", "DEC", "OBJECT", "FILTER",
        "depth", "AIRMASS", "seeing",
        "PROPID", "EXPNUM",
    ]

    raws = noirlab_api.search(
        noirlab_query.query(
            "raw", "object", outfields, 
            proposal=proposal
        )
    )
    raws = astropy.table.Table(raws)
    raws['AIRMASS'] = raws['AIRMASS'].astype(float)

    instcals = noirlab_api.search(
        noirlab_query.query(
            "instcal", "object", outfields, 
            proposal=proposal
        )
    )
    instcals = astropy.table.Table(instcals)
    instcals['AIRMASS'] = instcals['AIRMASS'].astype(float)

    caldats = sorted(list(set(list(map(lambda x : x['caldat'], raws)))))

    calibrations = []

    missing = []
    for caldat in caldats:
        images = list(filter(lambda x : x['caldat'] == caldat, raws))
        bands = sorted(list(set(list(map(lambda x : x['FILTER'].split(" ")[0], images)))))
        bias = noirlab_api.search(
            noirlab_query.query(
                "raw", "zero", outfields, 
                caldat=caldat
            )
        )
        calibrations.extend(bias)
        if len(bias) == 0:
            missing.append({"observation_type": "bias", "caldat": caldat, "band": None})
            print("no bias on", caldat, file=sys.stderr)
        for band in bands:
            flat = noirlab_api.search(
                noirlab_query.query(
                    "raw", "dome flat", outfields, 
                    caldat=caldat, band=band
                )
            )
            calibrations.extend(flat)
            if len(flat) == 0:
                missing.append({"observation_type": "flat", "caldat": caldat, "band": band})
                print("no flat for", band, "on", caldat, file=sys.stderr)
    
    missing = astropy.table.Table(missing)
    calibrations = astropy.table.Table(calibrations)
    calibrations['AIRMASS'] = calibrations['AIRMASS'].astype(float)

    exposures = astropy.table.vstack([raws, instcals, calibrations])
    exposures['dateobs_min'] = list(map(lambda x : astropy.time.Time(x, scale='utc', format='isot'), exposures['dateobs_min']))
    exposures['dateobs_midpoint'] = exposures['dateobs_min'] + astropy.time.TimeDelta(exposures['exposure']/2 + 0.5, format='sec')
    exposures['mjd'] = exposures['dateobs_min'].mjd
    exposures['mjd_midpoint'] = exposures['dateobs_midpoint'].mjd
    exposures['night'] = list(map(lambda x : int("".join(x.split("-"))), exposures['caldat']))
    coords = astropy.coordinates.SkyCoord(ra=exposures['RA'], dec=exposures['DEC'], unit=(u.hourangle, u.deg))
    exposures['RA(deg)'] = coords.ra
    exposures['DEC(deg)'] = coords.dec

    exposures['band'] = list(map(lambda x : x.split(" ")[0], exposures['FILTER']))

    return exposures, missing

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir")
    parser.add_argument("--proposal-id", "-p", default="2019A-0337")
    args = parser.parse_args()

    exposures_file = os.path.join(args.data_dir, "exposures.ecsv")
    missing_file = os.path.join(args.data_dir, "missing_data.ecsv")
    exposures, missing = survey_exposures(args.proposal_id)
    
    os.makedirs(args.data_dir, exist_ok=True)
    print("writing exposures to", exposures_file, file=sys.stderr)
    exposures.write(exposures_file, format='ascii.ecsv', overwrite=True)
    print("writing missing data to", missing_file, file=sys.stderr)
    missing.write(missing_file, format='ascii.ecsv', overwrite=True)

if __name__ == "__main__":
    main()
