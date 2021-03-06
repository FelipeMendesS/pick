#!/usr/bin/env bash

NAMESPACE="com.brufino.pick"
SCRIPT="pick.py"

# Get the directory of this script so we can execute the related python (http://stackoverflow.com/a/246128/212110)
function get_base_dir {
    local SOURCE=$0
    # Resolve $SOURCE until the file is no longer a symlink
    while [ -h "${SOURCE}" ]; do
      local BASEDIR="$(cd -P "$(dirname "${SOURCE}")" && pwd)"
      SOURCE="$(readlink "${SOURCE}")"
      # If $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
      [[ ${SOURCE} != /* ]] && SOURCE="${BASEDIR}/${SOURCE}"
    done
    BASEDIR="$(cd -P "$(dirname "${SOURCE}")" && pwd)"
    echo "${BASEDIR}"
}

if [[ -t 0 ]]; then
    echo "Run cell with piped input. E.g. ls -l | cell"
    exit 1
else
    BASEDIR="$(get_base_dir)"
    TMPFILE_IN="$(mktemp -t ${NAMESPACE})"
    TMPFILE_OUT="$(mktemp -t ${NAMESPACE})"
    tee "${TMPFILE_IN}" > /dev/null
    python "${BASEDIR}/${SCRIPT}" "${TMPFILE_IN}" "${TMPFILE_OUT}" "$@" < /dev/tty > /dev/tty
    EXITCODE=$?
    if [[ ${EXITCODE} -eq 0 && -f "${TMPFILE_OUT}" ]]; then
        cat "${TMPFILE_OUT}"
    fi
    rm "${TMPFILE_IN}"
    rm "${TMPFILE_OUT}"
    exit ${EXITCODE}
fi
