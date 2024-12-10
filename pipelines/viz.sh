#!/bin/bash
set -uex
yaml=$1
pipeline=$(basename $yaml | sed 's/.yaml//' | sed 's/#/\//')
d=$DEEP_PROJECT_DIR/pipelines/$pipeline
mkdir -p $d

pipetask build -p $yaml --pipeline-dot "$d/pipeline.dot"
cd $d
dot pipeline.dot -Tpng > pipeline.png
dot pipeline.dot -Tjpg > pipeline.jpg
dot pipeline.dot -Tsvg > pipeline.svg
dot pipeline.dot -Tpdf > pipeline.pdf