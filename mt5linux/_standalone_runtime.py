import uuid
import warnings


class StandaloneRuntime:
    _runtime_name = "standalone"

    def __init__(self):
        self._uuid = str(uuid.uuid4())
        self._name = None
        self._port = None
        self._ui_port = None
        self._host = None
        warnings.warn(
            "No container runtime detected. Attaching to externally-managed "
            "server without lifecycle management.",
            UserWarning,
            stacklevel=2,
        )

    def _create_connection_file(self) -> None:
        pass

    def _delete_connection_file(self) -> None:
        pass

    def _list_connection_files(self) -> list[str]:
        return []

    def _is_controlled_container(self) -> bool:
        return False

    def _create_controlled_container_file(self) -> None:
        pass

    def _check_image_exists(self, image: str) -> bool:
        return False

    def _pull_image(self, image: str) -> bool:
        return False

    def _get_container_by_port(self, port: int) -> None:
        return None

    def _get_stopped_container_by_port(self, port: int) -> None:
        return None

    def _start_existing_container(self, name: str) -> bool:
        return False

    def _run_container(
        self, name: str, image: str, ports: dict, env_vars: list
    ) -> bool:
        return False

    def start_container(
        self,
        host: str,
        port: int,
        image: str,
        mt5_login: str = None,
        mt5_password: str = None,
        mt5_server: str = None,
        ui_port: int = None,
        ui_password: str = None,
        ui_host: str = "0.0.0.0",
        vnc_port: int = 5901,
    ):
        self._host = host
        self._port = port
        self._ui_port = None
        self._ui_host = None

    def run(
        self,
        port: int,
        name: str,
        image: str = "lprett/mt5linux:local",
        mt5_login: str = None,
        mt5_password: str = None,
        mt5_server: str = None,
        vnc_password: str = None,
        novnc_port: int = None,
    ) -> bool:
        return False

    def _stop_container(self, name: str) -> bool:
        return False

    def stop(self, name: str) -> bool:
        return False

    def _remove_container(self, name: str) -> bool:
        return False

    def remove(self, name: str) -> bool:
        return False

    def _get_container_status(self, name: str) -> str:
        return "externally managed"

    def status(self, name: str) -> str:
        return "externally managed"

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_docker(self) -> bool:
        return False

    @property
    def is_udocker(self) -> bool:
        return False

    @property
    def is_standalone(self) -> bool:
        return True

    @property
    def container_name(self) -> str:
        return self._name

    @property
    def port(self) -> int:
        return self._port

    @property
    def ui_port(self) -> int:
        return self._ui_port
