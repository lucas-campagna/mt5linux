## Summary

This PR brings major Docker image optimization and automation improvements to mt5linux.

## Fixes

- Fixes #32

## Features

- Docker image reduced to 1/5 the size of the previous image
- Auto search server on initialize - no longer need to open the UI to search for the server
- `initialize()` accepts `server`, `login`, and `password` options for Docker environments
- Simplified README - no longer requires Python on Windows, uses standalone `mt5server.exe` binary
- Server default port `18812` documented

## Description

### Docker Image Optimization

- **Multi-stage build**: Reduced final image size significantly
- **Go websockify**: Replaced Python websockify (~50MB) with static Go binary (7.6MB)
- **Removed i386-windows**: Saved ~172MB by using `wine` instead of `wine64`
- **Pre-installed MT5**: Build-stage installation with symlinks at runtime
- **Tar archive approach**: Clean extraction of `/opt` folder at runtime
- **VC++ redistributable**: Added support for mt5server.exe dependencies

### New Architecture

- Go-based websockify implementation
- Pre-built `mt5server.exe` binary for faster startup
- RPyC server with auto-start and watchdog
- noVNC support with http-server (port 8080)
- Updated networking: 8080 (noVNC), 5901 (VNC), 18812 (RPyC)
- Portable mode support (`/portable` flag)

### Quality of Life

- Headless docker-compose with noVNC
- Auto-download/install MT5 if not found
- Bypass wine-mono prompt (`WINEDLLOVERRIDES`)
- Kill unnecessary Wine processes after startup
- Clean minimal workspace with `mt5cfg.ini`
- Mount `mt5cfg.ini` to `/app` for persistent config
