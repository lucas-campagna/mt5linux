from pickle import PicklingError
from typing import Literal

import rpyc

from mt5linux._runtime import create_runtime
from mt5linux.types import MT5_TYPE_TAG, materialize
from mt5linux.ui import UI

HELPER_CODE = '''
def _mt5linux_to_plain(obj):
    """Convert MT5 result objects (recursively) into pickle-friendly
    structures, tagging each with its original class name."""
    if hasattr(obj, "_asdict"):
        plain = {"__TAG__": type(obj).__name__}
        for key, value in obj._asdict().items():
            plain[key] = _mt5linux_to_plain(value)
        return plain
    if isinstance(obj, dict):
        return {key: _mt5linux_to_plain(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(_mt5linux_to_plain(item) for item in obj)
    return obj
'''.replace("__TAG__", MT5_TYPE_TAG)


# The exception-marshalling half of rpyc's own SlaveService.on_connect
# (rpyc/core/service.py). The classic path gets these flags for free because
# rpyc.classic.connect installs ClassicService, which applies them on connect.
# A hand-built connection does not, and so inherits rpyc's DEFAULT_CONFIG where
# every one of them is False.
#
# `instantiate_custom_exceptions` is the load-bearing one. Without it a remote
# PicklingError is rebuilt locally by rpyc.core.vinegar as a GenericException
# subclass that merely *prints* as "_pickle.PicklingError" -- isinstance() against
# the real PicklingError is False. The `except PicklingError` in eval() therefore
# cannot match it, and the issue-#57 materialize fallback is never reached, so
# every MT5 call returning a namedtuple fails under the standalone engine while
# the identical call succeeds under docker.
CLASSIC_CONNECTION_CONFIG = {
    "allow_all_attrs": True,
    "allow_pickle": True,
    "allow_getattr": True,
    "allow_setattr": True,
    "allow_delattr": True,
    "allow_exposed_attrs": False,
    "import_custom_exceptions": True,
    "instantiate_custom_exceptions": True,
    "instantiate_oldstyle_exceptions": True,
}


class ContainerManager:
    """
    Manages mt5linux container lifecycle.

    Provides methods to run, stop, remove containers and check their status.
    """

    def __init__(
        self,
        engine: Literal["auto", "docker", "udocker", "standalone"] = "auto",
        host: str = "0.0.0.0",
        port: int = 18812,
        timeout: int = 300,
        image_tag: str = "latest",
        mt5_login: str = None,
        mt5_password: str = None,
        mt5_server: str = None,
        ui_port: int = None,
        ui_password: str = None,
        ui_host: str = "0.0.0.0",
        vnc_port: int = 5901,
        materialized: bool = True,
    ):
        """
        Initialize ContainerManager and start container if needed.

        Args:
            engine: Container engine to use: 'auto', 'docker', 'udocker', or 'standalone'.
                'auto' uses docker if available, otherwise udocker, otherwise standalone.
                'standalone' attaches to an already-running RPyC server without managing
                any container. Default = 'auto'
            host: Host to connect to. Default = 0.0.0.0
            port: Port for RPyC connection. Default = 18812
            timeout: Sync request timeout. Default = 300
            image_tag: Docker image tag to use. Default = 'latest'
            mt5_login: MT5 account login for auto-login
            mt5_password: MT5 account password for auto-login
            mt5_server: MT5 trade server for auto-login
            ui_port: UI (noVNC) port. If not provided, finds first available.
            ui_password: UI password for the container. Default = None (no password)
            ui_host: UI (noVNC) host. Default = '0.0.0.0'
            vnc_port: VNC port. Default = 5901
            materialized: bool
                When True (default), MT5 result objects are reconstructed into
                typed frozen dataclasses from mt5linux.types, solving issue #57.
                When False, results are returned as plain dicts / netrefs
                without any reconstruction.
        """
        self._engine = engine
        self._host = host
        self._timeout = timeout
        self._image = f"lprett/mt5linux:{image_tag}"
        self._mt5_login = mt5_login
        self._mt5_password = mt5_password
        self._mt5_server = mt5_server
        self._ui_password = ui_password
        self._ui_host = ui_host
        self._vnc_port = vnc_port
        self._materialized = materialized

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
            ui_host=ui_host,
            vnc_port=vnc_port,
        )

        self._ui = None
        if engine == "standalone":
            self.__conn = self._connect_fallback(timeout=self._timeout)
        else:
            self.__conn = self._connect(timeout=self._timeout)
        self.__to_plain = self._install_conversion_helper() if materialized else None

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
        import socket
        import time

        start_time = time.time()
        last_error = None

        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
        try:
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
        finally:
            socket.setdefaulttimeout(original_timeout)

    def _connect_fallback(self, timeout: int = 60, retry_interval: int = 2) -> rpyc.Connection:
        """
        Fallback connect using rpyc.connect (no classic protocol) for servers
        that don't support module exposure.
        """
        import socket
        import time
        from rpyc.core.service import Service
        from rpyc.core.channel import Channel
        from rpyc.core.stream import SocketStream

        class MinimalService(Service):
            _conn = None

            def _install(self, conn, root):
                pass

            def on_connect(self, conn):
                self._conn = conn

            def eval(self, expr):
                return self._conn.eval(expr)

            def execute(self, code):
                self._conn.execute(code)

            @property
            def namespace(self):
                return self._conn.namespace if self._conn else {}

            def getmodule(self, name):
                import importlib
                return importlib.import_module(name)

        start_time = time.time()
        last_error = None

        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
        try:
            while time.time() - start_time < timeout:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(timeout)
                    s.connect((self.host, self.port))
                    stream = SocketStream(s)
                    channel = Channel(stream)
                    self.__conn = MinimalService()._connect(
                        channel, dict(CLASSIC_CONNECTION_CONFIG)
                    )
                    self.__conn._config["sync_request_timeout"] = timeout

                    def _eval(code):
                        return self.__conn.root.eval(code)

                    def _execute(code):
                        self.__conn.root.execute(code)

                    self.__conn.eval = _eval
                    self.__conn.execute = _execute
                    self._ui = None
                    print("Connected (fallback)")
                    return self.__conn
                except Exception as e:
                    last_error = e
                    time.sleep(retry_interval)

            raise TimeoutError(
                f"Failed to connect to container at {self._host}:{self._port} "
                f"after {timeout} seconds. Last error: {last_error}"
            )
        finally:
            socket.setdefaulttimeout(original_timeout)

    def _install_conversion_helper(self):
        """Install the server-side result conversion helper (issue #57).

        The helper converts MetaTrader5 result objects into plain tagged
        structures in a single round trip, so large results (e.g.
        symbols_get()) do not require per-item requests. Returns the helper
        as a netref, or None when the server does not accept it.
        """
        try:
            self.__conn.execute(HELPER_CODE)
            return self.__conn.eval("_mt5linux_to_plain")
        except Exception:
            return None

    def eval(self, code: str):
        """
        Evaluate code in the container and return the result.

        When materialized=True (default), results that cannot cross RPyC
        (MetaTrader5 C-extension result objects, issue #57) are converted
        server-side into plain tagged structures and reconstructed into the
        typed classes from mt5linux.types.

        When materialized=False, results are returned as-is from obtain()
        (plain dicts / netrefs — the pre-fix behaviour).

        Args:
            code: Python code to evaluate

        Returns:
            Result of the evaluation
        """
        raw = self.__conn.eval(code)
        try:
            return rpyc.classic.obtain(raw)
        except PicklingError:
            if not self._materialized:
                raise
        if self.__to_plain is None:
            return raw
        try:
            plain = rpyc.classic.obtain(self.__to_plain(raw))
        except Exception:
            return raw
        return materialize(plain)

    def execute(self, code: str):
        """
        Execute code in the container.

        Args:
            code: Python code to execute
        """
        self.__conn.execute(code)

    @property
    def engine(self) -> str:
        """Get the engine being used ('auto', 'docker', 'udocker', or 'standalone')."""
        return self._engine

    @property
    def runtime(self) -> Literal["docker", "udocker", "standalone"] | None:
        """Get the actual runtime being used ('docker', 'udocker', or 'standalone')."""
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

    def get_runtime(self) -> Literal["docker", "udocker", "standalone"] | None:
        """Get the container runtime."""
        return self._runtime

    def run(
        self,
        port: int,
        image_tag: str = "latest",
        mt5_login: str | None = None,
        mt5_password: str | None = None,
        mt5_server: str | None = None,
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
            name=self._runtime.container_name,
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
        return self._runtime.stop(self._runtime.container_name)

    def remove(self) -> bool:
        """
        Remove the mt5linux container.

        Returns:
            True if removed successfully, False otherwise
        """
        return self._runtime.remove(self._runtime.container_name)

    def status(self) -> str:
        """
        Get the current status of the container.

        Returns:
            Container status: 'running', 'exited', 'not found', etc.
        """
        return self._runtime.status(self._runtime.container_name)

    def is_running(self) -> bool:
        """Check if the container is currently running."""
        return self.status() == "running"
