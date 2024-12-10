BINDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export DEEP_PROJECT_DIR=$(dirname "$BINDIR")

domain_setup="${DEEP_PROJECT_DIR}/etc/$(hostname -d)/setup.sh"
if test -f "${domain_setup}"; then
    echo "loading config ${domain_setup}" 1>&2
    source "${domain_setup}"
fi
host_setup="${DEEP_PROJECT_DIR}/etc/$(hostname -f)/setup.sh"
if test -f "${host_setup}"; then
    echo "loading config ${host_setup}" 1>&2
    source "${host_setup}"
fi

source "${OPT_LSST_DIR}"/bin/opt_lsst.sh
source "${PROC_LSST_DIR}"/bin/proc_lsst.sh

opt_lsst setup w_2024_30 #w_2023_38
# proc_lsst setup
export PROC_LSST_PARSL_INSTALL_DIR=$DEEP_PROJECT_DIR/parsl
source "${PROC_LSST_DIR}"/bin/setup.sh

source "${DEEP_PROJECT_DIR}"/data/credentials
export PGUSER
export PGPASSWORD
export PGDATABASE
export NOIRLAB_USER
export NOIRLAB_PASS
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY

pathadd "${DEEP_PROJECT_DIR}"/bin
pythonpathadd "${DEEP_PROJECT_DIR}"/python

setup -j -r "${DEEP_PROJECT_DIR}/modules/obs_decam"
setup -j -r "${DEEP_PROJECT_DIR}/modules/ctrl_bps_parsl"
# setup -j -r "${DEEP_PROJECT_DIR}/modules/source_injection"

pathadd "${DEEP_PROJECT_DIR}"/env/bin
pythonpathadd "${DEEP_PROJECT_DIR}"/env
export LD_LIBRARY_PATH="${DEEP_PROJECT_DIR}/env:${LD_LIBRARY_PATH}"

export REPO="$DEEP_PROJECT_DIR/repo"