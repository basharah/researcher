#!/usr/bin/env bash
set -euo pipefail

# Start services with production configuration (low CPU usage)

usage() {
	cat <<EOF
Usage: $(basename "$0") [options]

Starts the full stack using docker-compose.prod.yml.

Options:
	--build              Build all images before starting (uses build-images.sh)
	--no-cache           Build without cache (implies --build)
	--api-base URL       API base to embed in frontend at build time (NEXT_PUBLIC_API_BASE)
	-h, --help           Show this help

Examples:
	./start-prod.sh
	./start-prod.sh --build
	./start-prod.sh --build --no-cache --api-base https://your-domain/api/v1
EOF
}

BUILD=false
NO_CACHE=false
API_BASE=""

while [[ $# -gt 0 ]]; do
	case "$1" in
		--build) BUILD=true; shift ;;
		--no-cache) BUILD=true; NO_CACHE=true; shift ;;
		--api-base) API_BASE="$2"; shift 2 ;;
		-h|--help) usage; exit 0 ;;
		*) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
	esac
done

echo "Starting services with production configuration..."
echo "Features:"
echo "  ✓ No file watching (--reload disabled)"
echo "  ✓ Resource limits (CPU and memory)"
echo "  ✓ Read-only volumes where possible"
echo "  ✓ Multiple workers for better performance"
echo ""

if [[ "$BUILD" == true ]]; then
	cmd=("$(dirname "$0")/build-images.sh")
	if [[ "$NO_CACHE" == true ]]; then cmd+=("--no-cache"); fi
	if [[ -n "$API_BASE" ]]; then cmd+=("--api-base" "$API_BASE"); fi
	echo "Building images: ${cmd[*]}"
	"${cmd[@]}"
fi

docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "Services starting..."
echo "Frontend:   http://localhost:3000"
echo "API Health: http://localhost:8000/api/v1/health"
echo "Flower:     http://localhost:5555"
echo ""
echo "Use 'docker-compose -f docker-compose.prod.yml logs -f' to view logs"
echo "Use 'docker-compose -f docker-compose.prod.yml down' to stop"
