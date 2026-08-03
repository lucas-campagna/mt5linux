import subprocess
from typing import Optional

from mt5linux._base_runtime import Runtime


def _is_udocker_available() -> bool:
    """Check if udocker CLI is available."""
    import shutil

    return shutil.which("udocker") is not None


class UdockerRuntime(Runtime):
    """
    Udocker container runtime operations.
    """

    def __init__(self):
        if not _is_udocker_available():
            raise RuntimeError("Udocker is not available. Please install udocker.")
        self._runtime_name = "udocker"
        super().__init__()

    def _check_image_exists(self, image: str) -> bool:
        """Check if a udocker image exists locally."""
        try:
            result = subprocess.run(
                ["udocker", "images"], capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                return False
            return image in result.stdout or image.split(":")[0] in result.stdout
        except Exception:
            return False

    def _pull_image(self, image: str) -> bool:
        """Pull a udocker image."""
        try:
            print(f"Pulling udocker image '{image}'...")
            result = subprocess.run(
                ["udocker", "pull", image], capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"Failed to pull image: {result.stderr}")
            return result.returncode == 0
        except Exception:
            return False

    def _get_container_by_port(self, port: int) -> Optional[str]:
        """Check if a udocker container is running on the specified port."""
        try:
            result = subprocess.run(
                ["udocker", "ps"], capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                return None

            container_name = f"mt5linux-{port}"
            for line in result.stdout.strip().split("\n"):
                if container_name in line:
                    return container_name
            return None
        except Exception:
            return None

    def _get_stopped_container_by_port(self, port: int) -> Optional[str]:
        """Check if a udocker container is stopped on the specified port."""
        try:
            container_name = f"mt5linux-{port}"
            result = subprocess.run(
                ["udocker", "ps", "-a"], capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                return None

            for line in result.stdout.strip().split("\n"):
                if container_name in line:
                    return container_name
            return None
        except Exception:
            return None

    def _start_existing_container(self, name: str) -> bool:
        """Start an existing container."""
        result = subprocess.run(
            ["udocker", "start", name], capture_output=True, text=True
        )
        return result.returncode == 0

    def _run_container(
        self, name: str, image: str, ports: dict, env_vars: list
    ) -> bool:
        """Run a container with the given parameters."""
        env_cmd = ""
        if env_vars:
            env_cmd = " && ".join([f"export {v}" for v in env_vars]) + " && "

        cmd = [
            "udocker",
            "run",
            "--user=root",
            "--exec-mode=PROOT",
            "--name",
            name,
        ]
        for port_map in ports.keys():
            cmd.extend(["-p", port_map])
        cmd.extend(
            [
                image,
                "/bin/bash",
                "-c",
                f"{env_cmd}/src/main.sh",
            ]
        )

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            self._create_connection_file()
        return result.returncode == 0

    def _create_connection_file(self) -> None:
        """Create a connection file in /tmp/connections/<uuid> inside the container."""
        conn_path = "/tmp/connections"
        subprocess.run(
            [
                "udocker",
                "run",
                "--exec-mode=PROOT",
                self._name,
                "/bin/bash",
                "-c",
                f"mkdir -p {conn_path} && touch {conn_path}/{self._uuid}",
            ],
            check=True,
        )

    def _delete_connection_file(self) -> None:
        """Delete the connection file in /tmp/connections/<uuid> inside the container."""
        conn_path = "/tmp/connections"
        subprocess.run(
            [
                "udocker",
                "run",
                "--exec-mode=PROOT",
                self._name,
                "/bin/bash",
                "-c",
                f"rm -f {conn_path}/{self._uuid}",
            ],
            check=True,
        )

    def _list_connection_files(self) -> list[str]:
        """List all connection files in /tmp/connections/ inside the container."""
        conn_path = "/tmp/connections"
        result = subprocess.run(
            [
                "udocker",
                "run",
                "--exec-mode=PROOT",
                self._name,
                "/bin/bash",
                "-c",
                f"ls -1 {conn_path}",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return []
        return [f for f in result.stdout.strip().split("\n") if f]

    def _stop_container(self, name: str) -> bool:
        """Stop a container."""
        result = subprocess.run(
            ["udocker", "stop", name], capture_output=True, text=True
        )
        return result.returncode == 0

    def _remove_container(self, name: str) -> bool:
        """Remove a container."""
        result = subprocess.run(["udocker", "rm", name], capture_output=True, text=True)
        return result.returncode == 0

    def _get_container_status(self, name: str) -> str:
        """Get the status of a container."""
        result = subprocess.run(["udocker", "ps", "-a"], capture_output=True, text=True)
        if result.returncode != 0:
            return "not found"
        for line in result.stdout.strip().split("\n"):
            if name in line:
                return "running" if "Up" in line else "stopped"
        return "not found"
