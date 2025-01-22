import argparse
from lsst.pipe.base.graph import QuantumGraph
from collections import Counter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("qgraph")

    args = parser.parse_args()

    qgraph = QuantumGraph.loadUri(args.qgraph)



    totals = {}
    for q in qgraph.inputQuanta:
        inputs = q.quantum.inputs['deepCoadd_directWarp']
        l = len(inputs)
        totals[l] = totals.get(l, 0) + 1


    cpu = lambda x : (9000/350) * x + 100
    mem = lambda x : (13/100) * x + 4
    for l in sorted(totals):
        print(l, totals[l], cpu(l), mem(l))

if __name__ == "__main__":
    main()

