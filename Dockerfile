# Railway n8n with Python and Playwright
FROM n8nio/n8n:latest

# Switch to root to install packages
USER root

# Install Python and dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    chromium \
    chromium-chromedriver \
    bash

# Create symlink for python
RUN ln -sf python3 /usr/bin/python

# Install Python packages
RUN pip3 install --no-cache-dir --break-system-packages \
    playwright

# Install Playwright browsers
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN python3 -m playwright install chromium
RUN python3 -m playwright install-deps chromium

# Copy calendar extraction script
COPY extract_childcarecrm.py /home/node/extract_childcarecrm.py

# Make script executable
RUN chmod +x /home/node/extract_childcarecrm.py

# Switch back to node user
USER node

# Expose n8n port
EXPOSE 5678

# Start n8n
CMD ["n8n"]
