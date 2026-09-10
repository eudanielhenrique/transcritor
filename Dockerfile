FROM --platform=linux/amd64 public.ecr.aws/e1h7x4a2/plow-cloud-agents:base-cd2a898d673812621bae6764560e455807e9818e@sha256:bfd4980f361a551e62569f8c2eb717c1076d0b8be3a0499b869eaece151336a4

# Agent Identity and Personality
COPY runtime/SOUL.md /var/lib/hermes/SOUL.md
COPY LICENSE /usr/share/doc/transcritor/

# Shipped at /opt/hermes/skills
COPY skills/ /opt/hermes/skills/

# Normalize permissions preserving executable bits
RUN find /opt/hermes/skills -mindepth 1 -type d -exec chmod 0755 {} + \
 && find /opt/hermes/skills -mindepth 1 -type f ! -perm -u+x -exec chmod 0644 {} + \
 && find /opt/hermes/skills -mindepth 1 -type f -perm -u+x -exec chmod 0755 {} + \
 && chmod 0644 /var/lib/hermes/SOUL.md

# Install python dependencies for transcription tools in the agent venv and create system symlinks
RUN uv pip install --python /opt/hermes/.venv yt-dlp youtube-transcript-api SpeechRecognition pydub requests python-dotenv \
 && ln -sf /opt/hermes/.venv/bin/yt-dlp /usr/local/bin/yt-dlp \
 && ln -sf /opt/hermes/.venv/bin/python3 /usr/local/bin/python \
 && ln -sf /opt/hermes/.venv/bin/python3 /usr/local/bin/python3

# The agent-index usage reporter client, pinned
COPY vendor/client.pin /opt/plow/agent-index-client.pin
RUN set -eu; \
    sha="$(sed -n 's/^sha=//p' /opt/plow/agent-index-client.pin)"; \
    want="$(sed -n 's/^sha256=//p' /opt/plow/agent-index-client.pin)"; \
    path="$(sed -n 's/^path=//p' /opt/plow/agent-index-client.pin)"; \
    curl -fsS --max-time 60 -o /opt/plow/agent-index-client.py \
      "https://raw.githubusercontent.com/plow-pbc/agent-index-client/${sha}/${path}"; \
    got="$(sha256sum /opt/plow/agent-index-client.py | cut -d' ' -f1)"; \
    [ "$got" = "$want" ] || { echo "agent-index client is $got, pin says $want" >&2; exit 1; }; \
    chmod 0644 /opt/plow/agent-index-client.py

# s6-overlay service definitions (includes agent-index usage reporter)
COPY image/s6-overlay/ /etc/s6-overlay/
