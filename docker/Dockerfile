FROM tobix/pywine:3.12

# Update and install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    x11vnc \
    xvfb \
    fluxbox \
    supervisor \
    cabextract \
    git \
    procps \
    python3-websockify \
    python3-numpy \
    xdotool \
    xautomation \
    wmctrl \
    expect \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /mt5linux
COPY requirements.txt ./

RUN wine pip install -r requirements.txt

RUN curl -L -o winetricks https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks && \
    chmod +x winetricks && \
    mv winetricks /usr/bin/ && \
    xvfb-run sh -c "winetricks --unattended vcrun2019"

RUN curl -L -o noVNC.zip https://github.com/novnc/noVNC/archive/refs/heads/master.zip && unzip noVNC.zip && rm noVNC.zip

COPY start.sh mt5cfg.ini test_connection.py install_mt5.sh mt5_watchdog.sh ./
RUN chmod +x ./start.sh ./install_mt5.sh ./mt5_watchdog.sh

ENTRYPOINT ["./start.sh"]
