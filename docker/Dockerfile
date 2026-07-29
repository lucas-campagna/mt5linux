# Builder stage - Install MT5 in Wine and clone noVNC
FROM alpine:3.20 AS builder

RUN apk add --no-cache \
    git \
    wine \
    xvfb \
    curl \
    jq

RUN mkdir -p /opt/wineprefix

# Download and install MetaTrader 5
RUN mkdir -p /tmp/mt5install && \
    curl -L -o /tmp/mt5install/mt5setup.exe https://download.mql5.com/cdn/web/metaquotes.ltd/mt5/mt5setup.exe && \
    Xvfb :99 -screen 0 1024x768x16 >/dev/null 2>&1 & \
    XVFB_PID=$! && \
    sleep 2 && \
    WINEDLLOVERRIDES="mscoree=" DISPLAY=:99 WINEPREFIX=/opt/wineprefix wine64 /tmp/mt5install/mt5setup.exe /auto /path:"C:/MT5" && \
    sleep 5 && \
    kill $XVFB_PID 2>/dev/null || true

# Download mt5server.exe from GitHub releases
RUN curl -s "https://api.github.com/repos/lucas-campagna/mt5linux/releases/latest" | \
    jq -r '.assets[] | select(.name | contains("mt5server")) | .browser_download_url' | \
    xargs -I {} curl -L -o /opt/wineprefix/drive_c/mt5server.exe {}

# Build Go websockify from source
RUN apk add --no-cache go git && \
    git clone --depth 1 --branch v1.2.0 https://github.com/msquee/go-websockify /tmp/go-websockify && \
    cd /tmp/go-websockify && \
    CGO_ENABLED=0 go build -o /opt/websockify .

# Clone noVNC
RUN git clone --depth 1 --branch v1.7.0 https://github.com/novnc/noVNC.git /opt/noVNC && \
    rm -rf /opt/noVNC/.git

# Download http-server from GitHub releases
RUN curl -s "https://api.github.com/repos/TheWaWaR/simple-http-server/releases/latest" | \
    jq -r '.assets[] | select((.name | contains("x86_64-unknown-linux-musl-simple")) and (.name | contains("sha") | not)) | .browser_download_url' | \
    xargs -I {} curl -L -o /opt/noVNC/http-server {}

RUN rm -rf /opt/wineprefix/drive_c/users/root/AppData/Roaming/MetaQuotes \
       /opt/wineprefix/drive_c/ProgramData/MetaQuotes \
       /opt/wineprefix/drive_c/MT5/uninstall.exe \
       /opt/wineprefix/drive_c/MT5/Profiles/Default/* \
       /opt/wineprefix/drive_c/MT5/Bases/Default
RUN tar czvf /opt.tar.gz /opt

# Runtime stage - Minimal Alpine image with Wine + MT5
FROM alpine:3.20

RUN apk add --no-cache \
    wine \
    xvfb \
    x11vnc \
    xdotool \
    curl

WORKDIR /app

COPY --from=builder /opt.tar.gz /app
COPY src/ /app/src/
RUN chmod +x /app/src/*.sh
RUN rm -rf /usr/lib/wine/i386-windows

ENV NOVNC_PORT=5901
ENV NOVNC_PAGE_PORT=8080
ENV RPYC_PORT=18812

EXPOSE 5901 8080 18812

ENTRYPOINT ["/app/src/main.sh"]
