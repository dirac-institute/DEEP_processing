set -u

cd $SCRATCH/DEEP_processing

exclude=(
    --exclude "raw" 
    --exclude "postISRCCD"
    --exclude "injected_postISRCCD"
    --exclude "postISRCCD_masked"
    --exclude "*icExp*" 
    --exclude "deepCoadd*Warp" 
    --exclude "overscanRaw" 
    --exclude "cpBiasIsrExp" 
    --exclude "cpFlatIsrExp"
    --exclude "deepDiff_templateExp"
    --exclude "deepDiff_matchedExp"
    --exclude "deepDiff_differenceTempExp"
)

d=$1
ssh epyc mkdir -p /epyc/data4/stampede/repo/${d}
rsync -avL ${exclude[@]} ./repo/${d}/ epyc:/epyc/data4/stampede/repo/${d} &

ssh epyc mkdir -p /epyc/data4/stampede/submit/${d}
rsync -avL ./submit/${d}/ epyc:/epyc/data4/stampede/submit/${d} &

wait
