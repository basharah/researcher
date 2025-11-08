#!/bin/bash

# Backwards-compatibility wrapper. Delegates to scripts/ version.
exec "$(dirname "$0")/scripts/test-extraction-endpoints.sh" "$@"
