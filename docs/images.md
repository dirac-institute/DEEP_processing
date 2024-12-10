Get exposure database:
```bash
$ python ./bin/exposures.py ./data
$ python bin/exposures_object_raw.py ./data/exposures.ecsv ./data/exposures_object_raw.ecsv
```

Download images:
```bash
$ python bin/download.py ./data/exposures.ecsv --download-dir ./data/images
```