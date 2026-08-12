.PHONY: help build build-nocache test-quick test-fast test-full shell clean

help:
	@echo "Trilinos Spack Packages - Docker Targets"
	@echo ""
	@echo "Build targets:"
	@echo "  make build          - Build Docker image with caching (recommended)"
	@echo "  make build-nocache  - Build Docker image without cache"
	@echo ""
	@echo "Test targets:"
	@echo "  make test-quick     - Run quick smoke tests (fastest)"
	@echo "  make test-fast      - Run all tests except slow installs"
	@echo "  make test-full      - Run full test suite"
	@echo ""
	@echo "Development:"
	@echo "  make shell          - Open interactive shell in container"
	@echo "  make clean          - Remove Docker images and volumes"
	@echo ""
	@echo "Docker Compose:"
	@echo "  docker-compose up test-quick"
	@echo "  docker-compose up test-fast"
	@echo "  docker-compose up test-full"

build:
	./docker-build.sh app

build-nocache:
	USE_CACHE=false ./docker-build.sh app

build-test:
	./docker-build.sh test

test-quick:
	./docker-run.sh quick

test-fast:
	./docker-run.sh fast

test-full:
	./docker-run.sh full

shell:
	./docker-run.sh shell

clean:
	@echo "Removing Docker images..."
	-docker rmi trilinos-spack-packages:base
	-docker rmi trilinos-spack-packages:spack-base
	-docker rmi trilinos-spack-packages:python-deps
	-docker rmi trilinos-spack-packages:app
	-docker rmi trilinos-spack-packages:latest
	-docker rmi trilinos-spack-packages:test
	@echo "Removing Docker volumes..."
	-docker volume rm trilinos-spack-packages_spack-cache
	-docker volume rm trilinos-spack-packages_test-results
	@echo "Clean complete!"
