# Multi-stage build for optimal caching and minimal test runtime
FROM registry.access.redhat.com/ubi9:latest AS base

# Disable all host repositories
RUN rm -rf /etc/rhsm-host

# Update base system
RUN yum -y --setopt=tsflags=nodocs update && yum clean all

# Install system dependencies (cached layer)
RUN yum -y install \
    gcc gcc-c++ gcc-gfortran \
    xz bzip2 patch diffutils file make \
    git python3-devel procps \
    environment-modules gettext unzip \
    libX11-devel cmake \
    ca-certificates \
    && yum clean all

# Update CA certificates
RUN update-ca-trust

# FIXME: Remove this someday
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /opt/trilinos-spack-packages

# ============================================
# Stage: Spack Setup (heavily cached)
# ============================================
FROM base AS spack-base

# Arguments for SSL handling (can be overridden at build time)
ARG DISABLE_SSL_VERIFY=false

# Clone and setup spack (this layer is cached unless spack version changes)
RUN if [ "$DISABLE_SSL_VERIFY" = "true" ]; then \
        git -c http.sslVerify=false clone --depth 1 https://github.com/spack/spack.git /opt/spack-src; \
    else \
        git clone --depth 1 https://github.com/spack/spack.git /opt/spack-src; \
    fi

# Pre-configure spack environment
ENV SPACK_ROOT=/opt/spack-src
ENV PATH="${SPACK_ROOT}/bin:${PATH}"

# Configure spack to handle SSL if needed
RUN if [ "$DISABLE_SSL_VERIFY" = "true" ]; then \
        mkdir -p /root/.spack && \
        echo "config:" > /root/.spack/config.yaml && \
        echo "  verify_ssl: false" >> /root/.spack/config.yaml && \
        echo "  connect_timeout: 60" >> /root/.spack/config.yaml; \
    fi

# Initialize spack shell support
RUN echo 'source /opt/spack-src/share/spack/setup-env.sh' >> /root/.bashrc

# Install core spack dependencies (cached layer - slowest step)
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    spack compiler find && \
    spack install -y python && \
    spack install -y py-pytest && \
    spack install -y cmake"

# ============================================
# Stage: Python Dependencies
# ============================================
FROM spack-base AS python-deps

# Copy only requirements first for optimal caching
COPY requirements.txt /opt/trilinos-spack-packages/

# Install Python test dependencies (cached if requirements.txt unchanged)
RUN pip3 install --no-cache-dir -r requirements.txt

# ============================================
# Stage: Application Code
# ============================================
FROM python-deps AS app

# Copy application code
COPY . /opt/trilinos-spack-packages/

# Add trilinos spack repository (uses local code)
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    spack repo add /opt/trilinos-spack-packages/spack_repo/trilinos"

# Load spack packages into environment
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    spack load python && \
    spack load py-pytest && \
    spack load cmake"

# Create entrypoint script
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'source /opt/spack-src/share/spack/setup-env.sh' >> /entrypoint.sh && \
    echo 'spack load python py-pytest cmake' >> /entrypoint.sh && \
    echo 'cd /opt/trilinos-spack-packages' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Default command runs fast tests
CMD ["pytest", "test/", "-m", "quick", "-n", "auto", "-v"]

# ============================================
# Stage: Test Runner (optional, for CI)
# ============================================
FROM app AS test

# This stage can be used for CI pipelines
# Build environment is ready, just run tests
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    spack load python py-pytest cmake && \
    cd /opt/trilinos-spack-packages && \
    pytest test/ -m quick -v"
