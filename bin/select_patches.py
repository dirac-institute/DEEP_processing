import re
import argparse
import sys
import lsst.daf.butler as dafButler
import astropy.table
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    parser.add_argument("--min", type=float, default=-float('inf'))
    parser.add_argument("--max", type=float, default=float('inf'))
    parser.add_argument("--sep", type=str, default=",")

    args = parser.parse_args()

    i = astropy.table.Table.read(args.input)
    m = (i['n'] > args.min) & (i['n'] <= args.max)
    o = args.sep.join(set(list(map(str, i[m]['patch']))))
    print(o)

if __name__ == "__main__":
    main()
