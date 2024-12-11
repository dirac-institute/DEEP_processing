#!/bin/bash

butler certify-calibrations $REPO DEEP/20190504/flat DEEP/20190505/calib/flat flat --begin-date 2000-01-01T00:00:00 --end-date 2050-01-01T00:00:00 --search-all-inputs
butler certify-calibrations $REPO DEEP/20201018/flat DEEP/20201019/calib/flat flat --begin-date 2000-01-01T00:00:00 --end-date 2050-01-01T00:00:00 --search-all-inputs
butler certify-calibrations $REPO DEEP/20220526/flat DEEP/20220525/calib/flat flat --begin-date 2000-01-01T00:00:00 --end-date 2050-01-01T00:00:00 --search-all-inputs
