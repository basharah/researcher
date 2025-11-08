#!/bin/bash

# Backwards-compatibility wrapper. Delegates to scripts/ version.
exec "$(dirname "$0")/scripts/test-phase4-integration.sh" "$@"
