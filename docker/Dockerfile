# Stage 1: Build stage - includes all build dependencies
FROM alpine:3.20 AS builder

# Install build dependencies
RUN apk add --no-cache \
    git \
    python3 \
    py3-pip \
    wine \
    xvfb \
    x11vnc \
    xdotool \
    gnutls \
    cabextract \
    curl

# Install websockify via pip
RUN pip3 install --no-cache-dir --break-system-packages websockify

# Clone noVNC and remove git history
RUN git clone --depth 1 https://github.com/novnc/noVNC.git /opt/noVNC && \
    rm -rf /opt/noVNC/.git

# Download and install winetricks for Windows dependencies
RUN curl -L -o /usr/bin/winetricks https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks && \
    chmod +x /usr/bin/winetricks

# Stage 2: Runtime stage - minimal image with only runtime dependencies
FROM alpine:3.20

# Install only runtime dependencies
RUN apk add --no-cache \
    wine \
    xvfb \
    x11vnc \
    xdotool \
    python3 \
    gnutls \
    cabextract

# Copy websockify and noVNC from builder
COPY --from=builder /usr/bin/websockify /usr/bin/
COPY --from=builder /usr/bin/winetricks /usr/bin/winetricks
COPY --from=builder /usr/lib/python3.12/site-packages/websockify /usr/lib/python3.12/site-packages/websockify
COPY --from=builder /usr/lib/python3.12/site-packages/websockify-0.13.0.dist-info /usr/lib/python3.12/site-packages/websockify-0.13.0.dist-info
COPY --from=builder /opt/noVNC /opt/noVNC

# Wine prefix directory
RUN mkdir -p /opt/wineprefix

# Copy startup script
COPY run_mt5.sh /run_mt5.sh
RUN chmod +x /run_mt5.sh

ENV DISPLAY=:0
ENV WINEPREFIX=/opt/wineprefix
ENV VNC_PORT=5900
ENV NOVNC_PORT=8080

EXPOSE 8080

ENTRYPOINT ["/run_mt5.sh"]
