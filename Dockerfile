# Use the inspect-tool-support image as base
FROM aisiuk/inspect-tool-support:latest

# Install numpy
RUN pip install --no-cache-dir numpy

# Set working directory
WORKDIR /workspace

# The base image already has Python and other tools needed for inspect evaluations