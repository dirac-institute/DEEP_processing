import astropy.table
import numpy as np
import matplotlib.pyplot as plt
import itertools
from pathlib import Path
import os

def grouped_table(t, k, c):
    o = []
    for g in t.group_by(k).groups:
        d = {}
        for col in c:
            d[col] = g[0][col]
        o.append(d)

    o = astropy.table.Table(o)
    return o

deep = Path(os.environ.get("DEEP_PROJECT_DIR"))
pedros_fakes = p = Path("/epyc/data4/fakesnoccd")
outdir = Path(__name__).parent / "derived"
outdir.mkdir(exist_ok=True)

def main():
    exposures = astropy.table.Table.read(deep / "data/exposures_object_raw.ecsv")
    exposures_all = astropy.table.Table.read(deep / "data/exposures.ecsv")
    exposures_all = exposures_all[exposures_all['proc_type'] == "instcal"]

    asteroid_orbits = astropy.table.Table.read(p / "asteroids.fits")
    asteroid_positions = astropy.table.Table.read(p / "asteroid_positions.fits")
    fakes_pre_binaries = astropy.table.Table.read(p / "fullcatalog_prebinary.fits")
    fakes_with_binaries = astropy.table.Table.read(p / "fakeswithbinaries.fits")
    tno_orbits = astropy.table.Table.read(p / "orbital_elements.fits")
    binary_properties = astropy.table.Table.read(p / "binaryorbits.fits")

    # ephemeris
    c = ['ORBITID', 'EXPNUM', 'RA', 'DEC', 'MAG', 'MJD_MID', 'TDB', 'r', 'd']
    asteroid_ephem = asteroid_positions[c]
    tno_ephem = fakes_pre_binaries[c]
    tno_ephem_with_binaries = fakes_with_binaries[c]

    asteroid_ephem.write(outdir / "asteroid_ephem.ecsv")
    tno_ephem.write(outdir / "tno_ephem.ecsv")
    tno_ephem_with_binaries.write(outdir / "tno_ephem_with_binaries.ecsv")

    # ingestion catalog
    c = ['ORBITID', 'EXPNUM', 'RA', 'DEC', 'MAG']
    ingest = astropy.table.Table.copy(asteroid_ephem[c])
    # differentiate Asteroids from TNOs
    ingest['ORBITID'] += int(1e7)
    # join asteroids + TNOs
    ingest = astropy.table.vstack([ingest, tno_ephem_with_binaries[c]])
    # add band information
    ingest = astropy.table.join(ingest, exposures[['EXPNUM', 'band']], keys=['EXPNUM'])
    # rename columns for LSST
    ingest.rename_columns(['RA', 'DEC', 'MAG'], ['ra', 'dec', 'mag'])
    # add source_type
    ingest['source_type'] = 'DeltaFunction'

    ingest.write(outdir / "ingest.ecsv")

    # population states
    c = ['ORBITID', 'aei', 'xv']
    asteroid_pop_states = asteroid_orbits[c]
    tno_pop_states = tno_orbits[c]

    asteroid_pop_states.write(outdir / "asteroid_population_states.ecsv")
    tno_pop_states.write(outdir / "tno_population_states.ecsv")

    # survey states
    c = ['ORBITID', 'aei', 'xv']
    asteroid_survey_states = grouped_table(asteroid_positions, "ORBITID", c)
    tno_survey_states = grouped_table(fakes_pre_binaries, "ORBITID", c)  

    asteroid_survey_states.write(outdir / "asteroid_survey_states.ecsv")
    tno_survey_states.write(outdir / "tno_survey_states.ecsv")

    # properties
    c = ['ORBITID', 'H_VR', 'AMP', 'PERIOD', 'PHASE']
    asteroid_properties = grouped_table(asteroid_positions, "ORBITID", c)
    tno_properties = grouped_table(fakes_pre_binaries, "ORBITID", c) 

    asteroid_properties.write(outdir / "asteroid_properties.ecsv")
    tno_properties.write(outdir / "tno_properties.ecsv")
    binary_properties.write(outdir / "binary_properties.ecsv")

if __name__ == "__main__":
    main()