from typing import Literal

from mt5linux._docker_runtime import DockerRuntime
from mt5linux._udocker_runtime import UdockerRuntime


def is_docker_available() -> bool:
    """Check if Docker CLI is available."""
    from mt5linux._docker_runtime import _is_docker_available

    return _is_docker_available()


def is_udocker_available() -> bool:
    """Check if udocker CLI is available."""
    from mt5linux._udocker_runtime import _is_udocker_available

    return _is_udocker_available()


def find_available_port(start_port: int = 18812, host: str = "127.0.0.1") -> int:
    """Find the first available port starting from start_port."""
    from mt5linux._base_runtime import find_available_port as _find_available_port

    return _find_available_port(start_port, host)


def create_runtime(engine: Literal["auto", "docker", "udocker"]) -> "Runtime":
    """
    Create the appropriate runtime instance based on engine.

    Args:
        engine: 'auto', 'docker', or 'udocker'

    Returns:
        DockerRuntime or UdockerRuntime instance

    Raises:
        RuntimeError: If no container runtime is available
    """
    from mt5linux._base_runtime import Runtime

    if engine == "docker":
        return DockerRuntime()
    elif engine == "udocker":
        return UdockerRuntime()
    elif engine == "auto":
        if is_docker_available():
            return DockerRuntime()
        elif is_udocker_available():
            return UdockerRuntime()
        else:
            raise RuntimeError(
                f"No container runtime available. engine='{
                    engine}' but neither docker nor udocker is installed."
            )
    raise RuntimeError(f"Invalid engine: {engine}")
