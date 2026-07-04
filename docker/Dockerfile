# Stage 1: Build stage - only need git to clone noVNC
FROM alpine:3.20 AS builder

# Clone noVNC (only thing needed from builder)
RUN apk add --no-cache git && \
    git clone --depth 1 https://github.com/novnc/noVNC.git /opt/noVNC && \
    rm -rf /opt/noVNC/.git

# Stage 2: Runtime stage - minimal image with only runtime dependencies
FROM alpine:3.20

# Install only runtime dependencies
RUN apk add --no-cache \
    wine \
    xvfb \
    x11vnc \
    curl \
    tar

# Copy noVNC from builder
COPY --from=builder /opt/noVNC /opt/noVNC

# Copy Go websockify binary
COPY websockify /usr/bin/websockify
RUN chmod +x /usr/bin/websockify

# Copy MT5 tarball to /app
COPY mt5.tar.gz /app/

# Create wineprefix directory
RUN mkdir -p /opt/wineprefix

# Copy startup script
COPY run_mt5.sh /run_mt5.sh
RUN chmod +x /run_mt5.sh

ENV DISPLAY=:0
ENV VNC_PORT=5900
ENV NOVNC_PORT=8080
ENV WINEPREFIX=/opt/wineprefix
WORKDIR /app

EXPOSE 8080

ENTRYPOINT ["/run_mt5.sh"]
