import subprocess
import socket
import uuid
from abc import ABC, abstractmethod
from typing import Optional, Literal


def _is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a port is in use on the specified host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True


def find_available_port(start_port: int = 18812, host: str = "127.0.0.1") -> int:
    """
    Find the first available port starting from start_port.

    Args:
        start_port: The port to start checking from (default 18812)
        host: The host to check on (default 127.0.0.1)

    Returns:
        The first available port number
    """
    port = start_port
    while _is_port_in_use(port, host):
        port += 1
    return port


class Runtime(ABC):
    """
    Base class for container runtime operations.
    """

    def __init__(self):
        if not hasattr(self, "_runtime_name"):
            self._runtime_name: Optional[str] = None
        self._uuid = str(uuid.uuid4())

    @abstractmethod
    def _create_connection_file(self) -> None:
        """Create a connection file in /tmp/connections/<uuid> inside the container."""
        raise NotImplementedError("Subclasses must implement _create_connection_file()")

    @abstractmethod
    def _delete_connection_file(self) -> None:
        """Delete the connection file in /tmp/connections/<uuid> inside the container."""
        raise NotImplementedError("Subclasses must implement _delete_connection_file()")

    @abstractmethod
    def _list_connection_files(self) -> list[str]:
        """List all connection files in /tmp/connections/."""
        raise NotImplementedError("Subclasses must implement _list_connection_files()")

    def __del__(self):
        if hasattr(self, "_name") and self._name:
            self._delete_connection_file()
            if not self._list_connection_files():
                import time

                time.sleep(5)
                if not self._list_connection_files():
                    self.stop(self._name)
                    self.remove(self._name)

    @property
    def name(self) -> Optional[str]:
        """Get the runtime name."""
        return self._runtime_name

    @property
    def is_docker(self) -> bool:
        """Check if runtime is docker."""
        return self._runtime_name == "docker"

    @property
    def is_udocker(self) -> bool:
        """Check if runtime is udocker."""
        return self._runtime_name == "udocker"

    @property
    def container_name(self) -> Optional[str]:
        """Get the container name."""
        return getattr(self, "_name", None)

    @property
    def port(self) -> Optional[int]:
        """Get the container port."""
        return getattr(self, "_port", None)

    @property
    def ui_port(self) -> Optional[int]:
        """Get the UI port."""
        return getattr(self, "_ui_port", None)

    @abstractmethod
    def _check_image_exists(self, image: str) -> bool:
        """Check if an image exists locally."""
        pass

    @abstractmethod
    def _pull_image(self, image: str) -> bool:
        """Pull an image."""
        pass

    @abstractmethod
    def _get_container_by_port(self, port: int) -> Optional[str]:
        """Check if a container is running on the specified port."""
        pass

    @abstractmethod
    def _get_stopped_container_by_port(self, port: int) -> Optional[str]:
        """Check if a container is stopped on the specified port."""
        pass

    @abstractmethod
    def _start_existing_container(self, name: str) -> bool:
        """Start an existing container."""
        pass

    @abstractmethod
    def _run_container(
        self, name: str, image: str, ports: dict, env_vars: list
    ) -> bool:
        """Run a container with the given parameters."""
        pass

    def start_container(
        self,
        host: str,
        port: int,
        image: str,
        mt5_login: Optional[str] = None,
        mt5_password: Optional[str] = None,
        mt5_server: Optional[str] = None,
        ui_port: int = None,
        ui_password: str = None,
        vnc_port: int = 5901,
    ):
        """
        Start a container, reusing existing one if available.

        Args:
            host: Host to connect to
            port: Requested port for RPyC connection
            image: Docker image to use
            mt5_login: MT5 account login
            mt5_password: MT5 account password
            mt5_server: MT5 trade server
            ui_port: UI (noVNC) port
            ui_password: UI password
            vnc_port: VNC port

        Raises:
            RuntimeError: If container fails to start
        """
        container = self._get_container_by_port(port)
        if container:
            self._name = container
            self._port = port
            self._ui_port = None
            return

        stopped = self._get_stopped_container_by_port(port)
        if stopped:
            print(f"Container '{stopped}' found stopped, starting it...")
            if self._start_existing_container(stopped):
                self._name = stopped
                self._port = port
                self._ui_port = None
                return
            raise RuntimeError(f"Failed to start stopped container {stopped}")

        self._ui_port = ui_port if ui_port else find_available_port(8080, host)
        self._port = find_available_port(port, host)
        self._name = f"mt5linux-{self._port}"

        if not self._check_image_exists(image):
            if not self._pull_image(image):
                raise RuntimeError(f"Failed to pull image {image}")

        env_vars = []
        if mt5_login:
            env_vars.append(f"MT5_LOGIN={mt5_login}")
        if mt5_password:
            env_vars.append(f"MT5_PASSWORD={mt5_password}")
        if mt5_server:
            env_vars.append(f"MT5_SERVER={mt5_server}")
        if ui_password:
            env_vars.append(f"UI_PASSWORD={ui_password}")
        env_vars.append(f"NOVNC_PORT={self._ui_port}")

        ports = {
            f"{self._ui_port}:8080": None,
            f"{self._port}:18812": None,
            f"{vnc_port}:{vnc_port}": None,
        }

        print(
            f"No container found on {host}:{port}. "
            f"Creating new container (UI: {self._ui_port}, MT5: {self._port})..."
        )

        if not self._run_container(self._name, image, ports, env_vars):
            raise RuntimeError(f"Failed to create container")

        print(f"Container '{self._name}' started")
        print(f"UI: http://{host}:{self._ui_port}")
        print(f"VNC: {host}:{vnc_port} (internal)")
        print(f"MT5: port={self._port}")

    def run(
        self,
        port: int,
        name: str,
        image: str = "lprett/mt5linux:local",
        mt5_login: Optional[str] = None,
        mt5_password: Optional[str] = None,
        mt5_server: Optional[str] = None,
        vnc_password: str = None,
        novnc_port: int = None,
    ) -> bool:
        """Run a new container with the specified parameters."""
        if not self._check_image_exists(image):
            if not self._pull_image(image):
                return False

        novnc_port = novnc_port if novnc_port else find_available_port(8080)

        env_vars = []
        if mt5_login:
            env_vars.append(f"MT5_LOGIN={mt5_login}")
        if mt5_password:
            env_vars.append(f"MT5_PASSWORD={mt5_password}")
        if mt5_server:
            env_vars.append(f"MT5_SERVER={mt5_server}")
        if vnc_password:
            env_vars.append(f"UI_PASSWORD={vnc_password}")
        env_vars.append(f"NOVNC_PORT={novnc_port}")

        ports = {
            f"{novnc_port}:8080": None,
            f"{port}:18812": None,
        }

        return self._run_container(name, image, ports, env_vars)

    @abstractmethod
    def _stop_container(self, name: str) -> bool:
        """Stop a container."""
        pass

    def stop(self, name: str) -> bool:
        """Stop a container."""
        return self._stop_container(name)

    @abstractmethod
    def _remove_container(self, name: str) -> bool:
        """Remove a container."""
        pass

    def remove(self, name: str) -> bool:
        """Remove a container."""
        return self._remove_container(name)

    @abstractmethod
    def _get_container_status(self, name: str) -> str:
        """Get the status of a container."""
        pass

    def status(self, name: str) -> str:
        """Get the status of a container."""
        return self._get_container_status(name)
