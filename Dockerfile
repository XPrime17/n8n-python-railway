FROM n8nio/n8n:latest

USER root

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

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip

RUN pip install playwright

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN playwright install chromium
RUN playwright install-deps chromium

RUN ln -sf python3 /usr/bin/python

COPY extract_childcarecrm.py /home/node/extract_childcarecrm.py

RUN chmod +x /home/node/extract_childcarecrm.py

USER node

EXPOSE 5678

CMD ["n8n"]
