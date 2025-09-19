import astropy.table
from pathlib import Path
import re
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix", type=Path)
    parser.add_argument("--collections", default=".*")
    parser.add_argument("--output", default=sys.stdout)
    parser.add_argument("--format", default="ascii.fast_csv")

    args = parser.parse_args()

    tables = []
    for path in args.prefix.rglob("size.csv"):
        collection = str(path.relative_to(args.prefix).parent)
        # print(collection)
        if re.compile(args.collections).match(collection):
            tables.append(astropy.table.Table.read(path))
    
    tables = astropy.table.vstack(tables)

    agg = []
    for g in tables.group_by("name").groups:
        agg.append(
            {
                "name": g[0]['name'],
                "size": g['size'].sum(),
                "datasets": g['datasets'].sum(),
            }
        )
    agg = astropy.table.Table(agg)

    if args.output != sys.stdout and args != sys.stderr:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    agg.write(args.output, format=args.format)

if __name__ == "__main__":
    main()
