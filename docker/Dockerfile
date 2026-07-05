# Builder stage - Clone noVNC
FROM alpine:3.20 AS builder
RUN apk add --no-cache git
RUN git clone --depth 1 https://github.com/novnc/noVNC.git /opt/noVNC && rm -rf /opt/noVNC/.git

# Runtime stage - Minimal Alpine image with Wine + pre-built mt5server binary
FROM alpine:3.20

RUN apk add --no-cache \
    wine \
    xvfb \
    x11vnc \
    curl \
    tar

RUN rm -rf /usr/lib/wine/i386-windows

COPY --from=builder /opt/noVNC /opt/noVNC

COPY docker/websockify /usr/bin/websockify
RUN chmod +x /usr/bin/websockify

COPY docker/mt5.tar.gz /app/
COPY docker/run_mt5.sh /run_mt5.sh
RUN chmod +x /run_mt5.sh

# Download pre-built mt5server binary from GitHub Releases
ARG MT5SERVER_VERSION=build-test
RUN curl -L -o /app/mt5server.exe "https://github.com/lucas-campagna/mt5linux/releases/download/${MT5SERVER_VERSION}/mt5server.exe"

RUN mkdir -p /opt/wineprefix

ENV DISPLAY=:0
ENV VNC_PORT=5900
ENV NOVNC_PORT=8080
ENV WINEPREFIX=/opt/wineprefix
ENV MT5_HOST=0.0.0.0
ENV RPYC_PORT=18812
WORKDIR /app

EXPOSE 8080 18812

ENTRYPOINT ["/run_mt5.sh"]
