export PROC_LSST_DIR="$INSTALL_PREFIX/proc_lsst"
export OPT_LSST_DIR="$INSTALL_PREFIX/opt_lsst"
export PATH="$INSTALL_PREFIX/opt_lsst/conda/envs/postgres/bin:$PATH"
export PROC_LSST_QUEUE="skx"
export PROC_LSST_SITE="stampede"

# export SCRUBBED_DIR="/gscratch/scrubbed/dirac/DEEP"
# export OPT_LSST_DIR="/gscratch/dirac/shared/opt/opt_lsst"

# function __klone_setup() {
#     unset http_proxy # Klone http proxy seems to conflicts with S3 access
#     export MINIO_HOST="epyc.astro.washington.edu"
#     export MINIO_PORT="8000"
#     export PGHOST="epyc.astro.washington.edu"
#     export PGPORT="5432"
# }

# function __mox_setup() {
#     # Set up tunnels to mox1 login node
#     # Need to access epyc.astro.washington.edu:8000 and epyc.astro.washington.edu:5432
#     # 5432
#     export MINIO_HOST="mox1.hyak.local"
#     export MINIO_PORT="58000"
#     export PGHOST="mox1.hyak.local"
#     export PGPORT="55432"
# }

# if [[ -n "${SLURM_CLUSTER_NAME}" ]]; then # on a Hyak compute node
#     echo "setting up ${SLURM_CLUSTER_NAME} compute node"
#     __"${SLURM_CLUSTER_NAME}"_setup
#     export J="${SLURM_CPUS_ON_NODE}"
# fi
