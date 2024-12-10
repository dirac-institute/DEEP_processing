Contents:
- `exposures.ecsv`: exposures associated with proposal ID. Generated with `bin/exposures.py`
- `missing_data.ecsv`: nights with no calibrations. Generated with `bin/exposures.py`
- `exposures_object_raw.ecsv`: a subset of `exposures.ecsv` where `obs_type = object` and `proc_type = raw`. Generated with `bin/exposures_object_raw.py`
- `images`: survey exposures downloaded with `bin/download.py`
- `refcats`: a link to LSST refcats
- `table*`: copies of tables from [DEEP II. Observational Strategy and Design](https://arxiv.org/pdf/2310.19864)