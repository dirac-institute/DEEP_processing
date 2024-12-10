def main():
    import argparse
    import astropy.table
    parser = argparse.ArgumentParser()
    parser.add_argument("exposures_file")
    parser.add_argument("out_file")

    args = parser.parse_args()

    e = astropy.table.Table.read(args.exposures_file)
    d = e[(e['obs_type'] == "object") & (e['proc_type'] == "raw")]
    d.sort("OBJECT")
    d.sort("EXPNUM")
    d.write(args.out_file, overwrite=True)

if __name__ == "__main__":
    main()
