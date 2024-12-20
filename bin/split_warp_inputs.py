import astropy.table

def make_subsets(t, n_max):
    t.sort("n")
    subsets = [[]]
    c = 0
    for r in t:
        c += r['n']
        if c > int(n_max):
            subsets[-1] = astropy.table.vstack(subsets[-1])
            subsets.append([r])
            c = r['n']
        else:
            subsets[-1].append(r)

    subsets[-1] = astropy.table.vstack(subsets[-1])
    return subsets

def main():
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser()

    parser.add_argument("input")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--group", action="store_true")
    parser.add_argument("--max-warps", type=int, default=int(1e4))

    args = parser.parse_args()

    t = astropy.table.Table.read(args.input)
    subsets = []
    if args.group:
        for g in t.group_by("n").groups:
            subsets.extend(make_subsets(g, args.max_warps))
    else:
        subsets.extend(make_subsets(t, args.max_warps))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for i, subset in enumerate(subsets):
        subset.write(args.output_dir / f"{i}.csv")

if __name__ == "__main__":
    main()
