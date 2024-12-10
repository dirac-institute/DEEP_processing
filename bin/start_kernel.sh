#!/usr/bin/env bash

BINDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "${BINDIR}/setup.sh"
exec python -m ipykernel $@
