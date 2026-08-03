import rpyc
from typing import Optional, Literal

from mt5linux.ui import UI
from mt5linux._runtime import create_runtime


class ContainerManager:
    """
    Manages mt5linux container lifecycle.

    Provides methods to run, stop, remove containers and check their status.
    """

    def __init__(
        self,
        engine: Literal["auto", "docker", "udocker"] = "auto",
        host: str = "0.0.0.0",
        port: int = 18812,
        timeout: int = 300,
        image_tag: str = "latest",
        mt5_login: str = None,
        mt5_password: str = None,
        mt5_server: str = None,
        ui_port: int = None,
        ui_password: str = None,
        vnc_port: int = 5901,
    ):
        """
        Initialize ContainerManager and start container if needed.

        Args:
            engine: Container engine to use: 'auto', 'docker', or 'udocker'.
                'auto' uses docker if available, otherwise udocker.
                Default = 'auto'
            host: Host to connect to. Default = 0.0.0.0
            port: Port for RPyC connection. Default = 18812
            timeout: Sync request timeout. Default = 300
            image_tag: Docker image tag to use. Default = 'latest'
            mt5_login: MT5 account login for auto-login
            mt5_password: MT5 account password for auto-login
            mt5_server: MT5 trade server for auto-login
            ui_port: UI (noVNC) port. If not provided, finds first available.
            ui_password: UI password for the container. Default = None (no password)
            vnc_port: VNC port. Default = 5901
        """
        self._engine = engine
        self._host = host
        self._timeout = timeout
        self._image = f"lprett/mt5linux:{image_tag}"
        self._mt5_login = mt5_login
        self._mt5_password = mt5_password
        self._mt5_server = mt5_server
        self._ui_password = ui_password
        self._vnc_port = vnc_port

        self._runtime = create_runtime(engine)

        self._runtime.start_container(
            host=host,
            port=port,
            image=self._image,
            mt5_login=mt5_login,
            mt5_password=mt5_password,
            mt5_server=mt5_server,
            ui_port=ui_port,
            ui_password=ui_password,
            vnc_port=vnc_port,
        )

        self._ui = None
        self.__conn = self._connect(timeout=self._timeout)

    def _connect(self, timeout: int = 60, retry_interval: int = 2) -> rpyc.Connection:
        """
        Connect to the container's RPyC server.

        Args:
            timeout: Maximum time to wait for connection in seconds. Default = 60
            retry_interval: Time between retry attempts in seconds. Default = 2

        Returns:
            RPyC Connection object

        Raises:
            TimeoutError: If connection cannot be established within timeout
        """
        import time

        start_time = time.time()
        last_error = None

        print("Connecting....")
        while time.time() - start_time < timeout:
            try:
                self.__conn = rpyc.classic.connect(self.host, self.port)
                self.__conn._config["sync_request_timeout"] = timeout
                self._ui = UI(self.__conn)
                print("Connected")
                return self.__conn
            except Exception as e:
                last_error = e
                time.sleep(retry_interval)

        raise TimeoutError(
            f"Failed to connect to container at {self._host}:{self._port} "
            f"after {timeout} seconds. Last error: {last_error}"
        )

    def eval(self, code: str):
        """
        Evaluate code in the container and return the result using rpyc.classic.obtain.

        Args:
            code: Python code to evaluate

        Returns:
            Result of the evaluation
        """
        return rpyc.classic.obtain(self.__conn.eval(code))

    def execute(self, code: str):
        """
        Execute code in the container.

        Args:
            code: Python code to execute
        """
        self.__conn.execute(code)

    @property
    def engine(self) -> str:
        """Get the engine being used ('auto', 'docker', or 'udocker')."""
        return self._engine

    @property
    def runtime(self) -> Optional[Literal["docker", "udocker"]]:
        """Get the actual runtime being used ('docker' or 'udocker')."""
        return self._runtime.name

    @property
    def name(self) -> str:
        """Get the container name."""
        return self._runtime.container_name

    @property
    def host(self) -> str:
        """Get the host."""
        return self._host

    @property
    def port(self) -> int:
        """Get the RPyC port."""
        return self._runtime.port

    @property
    def ui_port(self) -> int:
        """Get the UI (noVNC) port."""
        return self._runtime.ui_port

    @property
    def ui(self) -> int:
        """Get control over the UI."""
        return self._ui

    def get_runtime(self) -> Optional[Literal["docker", "udocker"]]:
        """Get the container runtime."""
        return self._runtime

    def run(
        self,
        port: int,
        image_tag: str = "latest",
        mt5_login: Optional[str] = None,
        mt5_password: Optional[str] = None,
        mt5_server: Optional[str] = None,
        vnc_password: str = None,
        novnc_port: int = None,
    ) -> bool:
        """
        Run the mt5linux container.

        Args:
            port: The port for RPyC connection
            image_tag: Docker image tag to use (default: 'latest')
            mt5_login: Optional MT5 login
            mt5_password: Optional MT5 password
            mt5_server: Optional MT5 server
            vnc_password: VNC password (default: None, no password)
            novnc_port: noVNC port (default: auto-select)

        Returns:
            True if container started successfully, False otherwise
        """
        return self._runtime.run(
            port=port,
            name=self._name,
            image=f"lprett/mt5linux:{image_tag}",
            mt5_login=mt5_login,
            mt5_password=mt5_password,
            mt5_server=mt5_server,
            vnc_password=vnc_password,
            novnc_port=novnc_port,
        )

    def stop(self) -> bool:
        """
        Stop the mt5linux container.

        Returns:
            True if stopped successfully, False otherwise
        """
        return self._runtime.stop(self._name)

    def remove(self) -> bool:
        """
        Remove the mt5linux container.

        Returns:
            True if removed successfully, False otherwise
        """
        return self._runtime.remove(self._name)

    def status(self) -> str:
        """
        Get the current status of the container.

        Returns:
            Container status: 'running', 'exited', 'not found', etc.
        """
        return self._runtime.status(self._name)

    def is_running(self) -> bool:
        """Check if the container is currently running."""
        return self.status() == "running"
