FROM node:20-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 git ca-certificates openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Install Hermes Agent from source
WORKDIR /opt/hermes-source
COPY . /opt/hermes-source/

RUN npm ci \
    && npm run build \
    && npm install -g /opt/hermes-source

ENV NODE_ENV=production
WORKDIR /app
EXPOSE 3000

# Render will provide $PORT
CMD ["node","server.js"]
