# Processing

## Biases
Make survey biases:
```
$ sbatch processing/stampede/bias.sh
```

Missing bias:
```
$ butler certify-calibrations $REPO DEEP/20201018/bias DEEP/20201019/calib/bias bias --begin-date 2000-01-01T00:00:00 --end-date 2050-01-01T00:00:00 --search-all-inputs
```

## Flats

Make survey flats:
```
$ sbatch processing/stampede/flat.sh
```

Missing flat:
```
# 20190505
$ butler certify-calibrations $REPO DEEP/20190504/flat DEEP/20190505/calib/flat flat --begin-date 2000-01-01T00:00:00 --end-date 2050-01-01T00:00:00 --search-all-inputs
# 20201019
$ butler certify-calibrations $REPO DEEP/20201018/flat DEEP/20201019/calib/flat flat --begin-date 2000-01-01T00:00:00 --end-date 2050-01-01T00:00:00 --search-all-inputs
# 20220525
$ butler certify-calibrations $REPO DEEP/20220526/flat DEEP/20220525/calib/flat flat --begin-date 2000-01-01T00:00:00 --end-date 2050-01-01T00:00:00 --search-all-inputs
```

## DRP

```
$ sbatch processing/stampede/drp.sh
```