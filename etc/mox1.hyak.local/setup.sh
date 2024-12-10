export PROC_LSST_DIR="/gscratch/dirac/shared/opt/proc_lsst"
export OPT_LSST_DIR="/gscratch/dirac/shared/opt/opt_lsst"

# export PGHOST="localhost"
# export PGPORT="55432"
# export MINIO_PORT="58000"
# export MINIO_HOST="localhost"

# if ! ps ux | grep ssh | grep "0.0.0.0:${PGPORT}" > /dev/null; then
#     echo "setting up tunnel to Epyc for Postgres on port ${PGPORT}" 1>&2
#     ssh -f -N -L "0.0.0.0:${PGPORT}:localhost:5432" epyc.astro.washington.edu || echo "cannot set up connection" 1>&2
# fi
# if ! ps ux | grep ssh | grep "0.0.0.0:${MINIO_PORT}" > /dev/null; then
#     echo "setting up tunnel to Epyc for Minio on port ${MINIO_PORT}" 1>&2
#     ssh -f -N -L "0.0.0.0:${MINIO_PORT}:localhost:8000" epyc.astro.washington.edu || echo "cannot set up connection" 1>&2
# fi

# export DEEP_PROCESSING_HOST="mox"
# export DEEP_PROCESSING_QUEUE="astro"
