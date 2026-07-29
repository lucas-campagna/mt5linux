## Summary

<!-- Brief description of the changes -->

## Fixes

- Fixes #32

## Features

- Docker image reduced to 1/5 the size of the previous image
- Auto search server on initialize - no longer need to open the UI to search for the server
- `initialize()` accepts `server`, `login`, and `password` options for Docker environments
- Simplified README - no longer requires Python on Windows, uses standalone `mt5server.exe` binary
- Server default port `18812` documented

## Checklist

- [ ] Tests pass
- [ ] Documentation updated
- [ ] Docker image builds successfully
