FROM mcr.microsoft.com/vscode/devcontainers/python:3.11

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y --no-install-recommends curl ca-certificates gnupg2 lsb-release apt-transport-https \
  && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft.gpg \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -fsSL -o /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/v1.27.3/bin/linux/amd64/kubectl \
  && chmod +x /usr/local/bin/kubectl

# Install kind
RUN curl -fsSL -o /usr/local/bin/kind "https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64" \
  && chmod +x /usr/local/bin/kind

# Install GitHub CLI (gh)
RUN set -eux; \
  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg; \
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list; \
  apt-get update; apt-get install -y gh; \
  rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/local/bin:$PATH"
