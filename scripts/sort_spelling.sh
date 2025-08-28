#!/bin/bash

ALLOW_FILE=".github/actions/spelling/allow.txt"

echo "Sorting spelling allow list..."
[ -f "${ALLOW_FILE}" ] || {
  echo "ERROR: Allow list not found: ${ALLOW_FILE}"
  exit 1
}
LC_ALL=C sort -u -o "${ALLOW_FILE}" "${ALLOW_FILE}"
