.PHONY: help build build-nocache test-quick test-fast test-full shell clean

help:
	@echo "Trilinos Spack Packages - Container Targets (Podman/Docker)"
	@echo ""
	@echo "Build targets:"
	@echo "  make build          - Build container image with caching (recommended)"
	@echo "  make build-nocache  - Build container image without cache"
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
	@echo "Compose (podman-compose or docker-compose):"
	@echo "  podman-compose up test-quick"
	@echo "  podman-compose up test-fast"
	@echo "  podman-compose up test-full"

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
	@echo "Removing container images..."
	@if command -v podman &> /dev/null; then \
		podman rmi trilinos-spack-packages:base || true; \
		podman rmi trilinos-spack-packages:spack-base || true; \
		podman rmi trilinos-spack-packages:python-deps || true; \
		podman rmi trilinos-spack-packages:app || true; \
		podman rmi trilinos-spack-packages:latest || true; \
		podman rmi trilinos-spack-packages:test || true; \
		echo "Removing volumes..."; \
		podman volume rm trilinos-spack-packages_spack-cache || true; \
		podman volume rm trilinos-spack-packages_test-results || true; \
	elif command -v docker &> /dev/null; then \
		docker rmi trilinos-spack-packages:base || true; \
		docker rmi trilinos-spack-packages:spack-base || true; \
		docker rmi trilinos-spack-packages:python-deps || true; \
		docker rmi trilinos-spack-packages:app || true; \
		docker rmi trilinos-spack-packages:latest || true; \
		docker rmi trilinos-spack-packages:test || true; \
		echo "Removing volumes..."; \
		docker volume rm trilinos-spack-packages_spack-cache || true; \
		docker volume rm trilinos-spack-packages_test-results || true; \
	fi
	@echo "Clean complete!"
