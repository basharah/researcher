#!/usr/bin/env bash
set -euo pipefail

# Build all service images for production compose
# Options:
#   -p, --push           Push images after build
#   -n, --no-cache       Do not use cache when building
#   -t, --tag [TAG]      Tag suffix to append (e.g., :v1). Default is :latest
#   -r, --registry [R]   Registry prefix (e.g., ghcr.io/owner/). Default is none
#   --platform [PLAT]    Target platform (e.g., linux/amd64). Default docker default
#   -f, --file [FILE]    Compose file to use (default docker-compose.prod.yml)
#   --api-base [URL]     Frontend API base to embed at build (NEXT_PUBLIC_API_BASE)
#   -h, --help           Show help

TAG="latest"
PUSH=false
NO_CACHE=false
REGISTRY=""
PLATFORM=""
COMPOSE_FILE="docker-compose.prod.yml"
API_BASE=""

usage() {
  cat <<EOF
Usage: $(basename "$0") [options]

Builds Docker images for all services in this repo.

Options:
  -p, --push              Push images after build
  -n, --no-cache          Do not use cache when building
  -t, --tag TAG           Tag suffix (default: latest)
  -r, --registry REG      Registry prefix (e.g. ghcr.io/you/)
  --platform PLAT         Build for platform (e.g. linux/amd64)
  -f, --file FILE         Compose file (default: docker-compose.prod.yml)
  --api-base URL          NEXT_PUBLIC_API_BASE to embed in frontend build
  -h, --help              Show this help message

Examples:
  ./build-images.sh
  ./build-images.sh -n -t v1
  ./build-images.sh -r ghcr.io/you/ -t 2025-11-11 --push
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--push) PUSH=true; shift ;;
    -n|--no-cache) NO_CACHE=true; shift ;;
    -t|--tag) TAG="$2"; shift 2 ;;
    -r|--registry) REGISTRY="$2"; shift 2 ;;
    --platform) PLATFORM="$2"; shift 2 ;;
    -f|--file) COMPOSE_FILE="$2"; shift 2 ;;
    --api-base) API_BASE="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

cd "$(dirname "$0")"

# Map service names to build contexts and image names
# Keep in sync with docker-compose.prod.yml
services=(
  "document-processing:services/document-processing researcher-document-processing-service"
  "vector-db:services/vector-db researcher-vector-db-service"
  "llm-service:services/llm-service researcher-llm-service"
  "api-gateway:services/api-gateway researcher-api-gateway-service"
  "frontend:frontend researcher-frontend"
)

build_arg_platform=()
if [[ -n "$PLATFORM" ]]; then
  build_arg_platform=("--platform" "$PLATFORM")
fi

no_cache_flag=()
if [[ "$NO_CACHE" == true ]]; then
  no_cache_flag=("--no-cache")
fi

# Build shared base image first
BASE_IMAGE="researcher-base:3.11-slim"
echo "\n==> Building base image $BASE_IMAGE from Dockerfile.base"
docker build "${build_arg_platform[@]}" "${no_cache_flag[@]}" \
  -f Dockerfile.base \
  -t "$BASE_IMAGE" \
  .

for entry in "${services[@]}"; do
  IFS=":" read -r svc ctx_and_img <<< "$entry"
  ctx="${ctx_and_img%% *}"
  img="${ctx_and_img#* }"
  full_image="${REGISTRY}${img}:${TAG}"

  echo "\n==> Building $svc ($full_image) from $ctx"
  # Extra build args for specific services
  extra_args=()
  if [[ "$svc" == "frontend" ]]; then
    if [[ -n "$API_BASE" ]]; then
      extra_args+=("--build-arg" "NEXT_PUBLIC_API_BASE=$API_BASE")
    fi
  fi

  docker build "${build_arg_platform[@]}" "${no_cache_flag[@]}" \
    "${extra_args[@]}" \
    -t "$full_image" \
    "$ctx"

  # Also tag :latest if a custom tag was used
  if [[ "$TAG" != "latest" ]]; then
    docker tag "$full_image" "${REGISTRY}${img}:latest"
  fi

  if [[ "$PUSH" == true ]]; then
    echo "Pushing $full_image"
    docker push "$full_image"
    if [[ "$TAG" != "latest" ]]; then
      docker push "${REGISTRY}${img}:latest"
    fi
  fi

done

echo "\nAll images built successfully."
