FROM ubuntu:latest

# Install basic tools and curl
RUN apt-get update && apt-get install -y \
    curl && \
    rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /uv-installer.sh

RUN sh /uv-installer.sh && rm /uv-installer.sh

# Set working directory
WORKDIR /opt
# Create virtual environment and install dependencies
ENV PATH="/root/.local/bin/:$PATH"

CMD ["uv","run", "main.py"]