
FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install Node.js 20, Python, and dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Create node user
RUN useradd -m -s /bin/bash node

# Install n8n globally
RUN npm install -g n8n

# Install Python packages
RUN pip3 install playwright

# Install Playwright browsers and dependencies
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN python3 -m playwright install chromium
RUN python3 -m playwright install-deps chromium

# Copy calendar extraction script
COPY extract_childcarecrm.py /home/node/extract_childcarecrm.py
RUN chmod +x /home/node/extract_childcarecrm.py

# Switch to node user
USER node
WORKDIR /home/node

# Set n8n environment variables
ENV N8N_USER_FOLDER=/home/node/.n8n
ENV N8N_PORT=5678

# Expose port
EXPOSE 5678

# Start n8n
CMD ["n8n"]
