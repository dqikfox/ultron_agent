#!/bin/bash

# ULTRON Agent 3.0 - Build Script
# Automates Docker image building for deployment
# Usage: ./build.sh [--no-cache] [--push] [--version <version>]

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="ultron-agent"
REGISTRY="${DOCKER_REGISTRY:-docker.io}"
VERSION="${VERSION:-3.0.0}"
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Flags
NO_CACHE=""
PUSH_IMAGE=false
VERSION_OVERRIDE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --push)
            PUSH_IMAGE=true
            shift
            ;;
        --version)
            VERSION="$2"
            VERSION_OVERRIDE=true
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}ULTRON Agent 3.0 - Docker Build Script${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# Pre-build checks
echo -e "\n${YELLOW}[*] Running pre-build checks...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}[!] Docker is not installed or not in PATH${NC}"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo -e "${RED}[!] Cannot connect to Docker daemon${NC}"
    exit 1
fi

# Check for Dockerfile
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}[!] Dockerfile not found in current directory${NC}"
    exit 1
fi

echo -e "${GREEN}[✓] Docker is available${NC}"
echo -e "${GREEN}[✓] Dockerfile found${NC}"

# Build information
echo -e "\n${YELLOW}[*] Build Information:${NC}"
echo "  Image Name:     $IMAGE_NAME"
echo "  Registry:       $REGISTRY"
echo "  Version:        $VERSION"
echo "  Git Commit:     $GIT_COMMIT"
echo "  Build Date:     $BUILD_DATE"
echo "  No Cache:       ${NO_CACHE:-false}"
echo "  Push After:     $PUSH_IMAGE"

# Build Docker image
echo -e "\n${YELLOW}[*] Building Docker image...${NC}"

BUILD_TAG="$REGISTRY/$IMAGE_NAME:$VERSION"
BUILD_TAG_LATEST="$REGISTRY/$IMAGE_NAME:latest"

docker build \
    $NO_CACHE \
    --tag "$BUILD_TAG" \
    --tag "$BUILD_TAG_LATEST" \
    --build-arg BUILD_DATE="$BUILD_DATE" \
    --build-arg GIT_COMMIT="$GIT_COMMIT" \
    --build-arg VERSION="$VERSION" \
    .

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}[✓] Docker image built successfully${NC}"
else
    echo -e "\n${RED}[!] Docker image build failed${NC}"
    exit 1
fi

# Show image information
echo -e "\n${YELLOW}[*] Image Information:${NC}"
docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.Created}}"

# Optional: Push to registry
if [ "$PUSH_IMAGE" = true ]; then
    echo -e "\n${YELLOW}[*] Pushing image to registry...${NC}"

    docker push "$BUILD_TAG"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] Image pushed successfully: $BUILD_TAG${NC}"
    else
        echo -e "${RED}[!] Image push failed${NC}"
        exit 1
    fi

    docker push "$BUILD_TAG_LATEST"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] Image pushed successfully: $BUILD_TAG_LATEST${NC}"
    else
        echo -e "${RED}[!] Image push failed${NC}"
        exit 1
    fi
fi

# Display next steps
echo -e "\n${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}[✓] Build Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Start services with docker-compose:"
echo "   docker-compose up -d"
echo ""
echo "2. View logs:"
echo "   docker-compose logs -f ultron-agent"
echo ""
echo "3. Check health:"
echo "   curl http://localhost:5000/health"
echo ""
echo "4. Stop services:"
echo "   docker-compose down"
echo ""

if [ "$PUSH_IMAGE" = false ]; then
    echo -e "${YELLOW}Note: Image was not pushed to registry.${NC}"
    echo "Use --push flag to push to registry:"
    echo "  ./build.sh --push"
fi

echo -e "\n${GREEN}Build script completed successfully!${NC}"
