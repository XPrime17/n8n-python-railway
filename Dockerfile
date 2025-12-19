# Railway n8n with Python and Playwright - FIXED VERSION
FROM n8nio/n8n:latest

# Switch to root to install packages
USER root

# Install Python, pip, and build dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    curl \
    git \
    build-base \
    python3-dev \
    libffi-dev \
    openssl-dev

# Create virtual environment to avoid conflicts
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip in virtual environment
RUN pip install --upgrade pip

# Install playwright and its dependencies in the virtual environment
RUN pip install playwright

# Set Playwright to use system installation
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install Playwright browsers and system dependencies
RUN playwright install chromium
RUN playwright install-deps chromium

# Create symlink so 'python' command works
RUN ln -sf python3 /usr/bin/python

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
```

4. Scroll down and click **"Commit changes"**
5. Add commit message: "Fix Playwright installation"
6. Click **"Commit changes"**

---

## Railway Will Auto-Rebuild

**Railway automatically watches your GitHub repo!**

Once you commit the changes:
- Railway will detect the update
- Automatically start a new build
- This will take 5-7 minutes

**You should see:**
- A new deployment starting in Railway
- Build logs showing the new attempt

---

## 🔍 Watch the Build

**In Railway:**

1. Go to your **n8n-python-railway** service
2. Click **"Deployments"** tab
3. You'll see a new deployment starting
4. Click on it to watch the logs

**Look for:**
```
✓ Installing Playwright...
✓ Installing Chromium...
✓ Build successful
