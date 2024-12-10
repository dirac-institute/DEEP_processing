#!/bin/bash

BINDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "${BINDIR}"/setup.sh
mkdir -p "${DEEP_PROJECT_DIR}/data/$(hostname)/kernel"
python -c "import json; print(json.dumps(dict(argv=[\"${DEEP_PROJECT_DIR}/bin/start_kernel.sh\", \"-f\", \"{connection_file}\"], display_name=\"DEEP2\", language=\"python\")))" > "${DEEP_PROJECT_DIR}/data/$(hostname)/kernel/kernel.json"
jupyter kernelspec install --user --replace --name "DEEP2" "${DEEP_PROJECT_DIR}/etc/$(hostname)/kernel"
