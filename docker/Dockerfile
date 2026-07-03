FROM alpine:3.20

# Install 64-bit Wine, Xvfb, x11vnc, Python, pip, and git
RUN apk add --no-cache \
    xvfb \
    x11vnc \
    python3 \
    py3-pip \
    git \
    wine

# Install websockify via pip
RUN pip3 install --no-cache-dir --break-system-packages websockify

# noVNC (minimal clone, no git history)
RUN git clone --depth 1 https://github.com/novnc/noVNC.git /opt/noVNC && \
    rm -rf /opt/noVNC/.git

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
