# Builder stage - Clone noVNC and install Python in Wine
FROM alpine:3.20 AS builder

RUN apk add --no-cache \
    git \
    wine \
    xvfb \
    curl \
    python3 \
    py3-pip

RUN mkdir -p /opt/wineprefix

# Install Python 3.11 for Windows
RUN mkdir -p /tmp/python-install && \
    curl -L -o /tmp/python-install/python-installer.exe https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe && \
    Xvfb :99 -screen 0 1024x768x16 >/dev/null 2>&1 & \
    XVFB_PID=$! && \
    sleep 2 && \
    WINEDLLOVERRIDES="mscoree=" DISPLAY=:99 WINEPREFIX=/opt/wineprefix wine /tmp/python-install/python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 TargetDir=C:\\Python311 && \
    sleep 5 && \
    kill $XVFB_PID 2>/dev/null || true

# Install mt5linux in wine python
RUN Xvfb :99 -screen 0 1024x768x16 >/dev/null 2>&1 & \
    XVFB_PID=$! && \
    sleep 2 && \
    WINEDLLOVERRIDES="mscoree=" DISPLAY=:99 WINEPREFIX=/opt/wineprefix wine C:\\Python311\\python.exe -m pip install --upgrade pip && \
    WINEDLLOVERRIDES="mscoree=" DISPLAY=:99 WINEPREFIX=/opt/wineprefix wine C:\\Python311\\python.exe -m pip install mt5linux && \
    kill $XVFB_PID 2>/dev/null || true

# Clone noVNC
RUN git clone --depth 1 https://github.com/novnc/noVNC.git /opt/noVNC && \
    rm -rf /opt/noVNC/.git

# Runtime stage - Minimal Alpine image with Wine + Python + mt5linux
FROM alpine:3.20

RUN apk add --no-cache \
    wine \
    xvfb \
    x11vnc \
    curl \
    tar

RUN rm -rf /usr/lib/wine/i386-windows

COPY --from=builder /opt/wineprefix /opt/wineprefix
COPY --from=builder /opt/noVNC /opt/noVNC

COPY docker/websockify /usr/bin/websockify
RUN chmod +x /usr/bin/websockify

COPY docker/mt5.tar.gz /app/
COPY docker/run_mt5.sh /run_mt5.sh
RUN chmod +x /run_mt5.sh

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
