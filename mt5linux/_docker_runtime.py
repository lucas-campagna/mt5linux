import subprocess
import os
import tempfile
from typing import Optional

from mt5linux._base_runtime import Runtime


def _is_docker_available() -> bool:
    """Check if Docker CLI is available."""
    import shutil

    return shutil.which("docker") is not None


class DockerRuntime(Runtime):
    """
    Docker container runtime operations.
    """

    def __init__(self):
        if not _is_docker_available():
            raise RuntimeError(
                "Docker is not available. Please install Docker.")
        self._runtime_name = "docker"
        super().__init__()

    def _check_image_exists(self, image: str) -> bool:
        """Check if a Docker image exists locally."""
        try:
            result = subprocess.run(
                ["docker", "image", "inspect", image], capture_output=True, check=False
            )
            return result.returncode == 0
        except Exception:
            return False

    def _pull_image(self, image: str) -> bool:
        """Pull a Docker image."""
        try:
            print(f"Pulling Docker image '{image}'...")
            result = subprocess.run(
                ["docker", "pull", image], capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"Failed to pull image: {result.stderr}")
            return result.returncode == 0
        except Exception:
            return False

    def _get_container_by_port(self, port: int) -> Optional[str]:
        """Check if a Docker container is running on the specified port by image and port."""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format",
                    "{{.Names}}|{{.Ports}}|{{.Image}}"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return None

            for line in result.stdout.strip().split("\n"):
                parts = line.split("|")
                if len(parts) < 3:
                    continue
                name, ports, image = parts
                if not image.startswith("lprett/mt5linux:"):
                    continue
                if (
                    f":{port}" in ports
                    or f"{port}/tcp" in ports
                    or f"{port}/udp" in ports
                ):
                    return name
            return None
        except Exception:
            return None

    def _get_stopped_container_by_port(self, port: int) -> Optional[str]:
        """Check if a Docker container is stopped on the specified port by image and port."""
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--format",
                    "{{.Names}}|{{.Ports}}|{{.Image}}"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return None

            for line in result.stdout.strip().split("\n"):
                parts = line.split("|")
                if len(parts) < 3:
                    continue
                name, ports, image = parts
                if not image.startswith("lprett/mt5linux:"):
                    continue
                if (
                    f":{port}" in ports
                    or f"{port}/tcp" in ports
                    or f"{port}/udp" in ports
                ):
                    return name
            return None
        except Exception:
            return None

    def _start_existing_container(self, name: str) -> bool:
        """Start an existing container."""
        result = subprocess.run(
            ["docker", "start", name], capture_output=True, text=True
        )
        return result.returncode == 0

    def _run_container(
        self, name: str, image: str, ports: dict, env_vars: list
    ) -> bool:
        """Run a container with the given parameters."""
        cmd = ["docker", "run", "-d", "--name", name]
        for port_map in ports.keys():
            cmd.extend(["-p", port_map])
        cmd.extend([f"-e {e}" for e in env_vars])
        cmd.append(image)

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            self._create_connection_file()
        return result.returncode == 0

    def _create_connection_file(self) -> None:
        """Create a connection file in /tmp/connections/<uuid> inside the container."""
        conn_path = "/tmp/connections"
        subprocess.run(
            [
                "docker",
                "exec",
                self._name,
                "sh",
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
                "docker",
                "exec",
                self._name,
                "sh",
                "-c",
                f"rm -f {conn_path}/{self._uuid}",
            ],
            check=True,
        )

    def _list_connection_files(self) -> list[str]:
        """List all connection files in /tmp/connections/ inside the container."""
        conn_path = "/tmp/connections"
        result = subprocess.run(
            ["docker", "exec", self._name, "sh", "-c", f"ls -1 {conn_path}"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return []
        return [f for f in result.stdout.strip().split("\n") if f]

    def _is_controlled_container(self) -> bool:
        """Check if this container was instantiated using this class or a child class."""
        result = subprocess.run(
            [
                "docker",
                "exec",
                self._name,
                "sh",
                "-c",
                "[ -f /tmp/controlled_container ]",
            ],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def _create_controlled_container_file(self) -> None:
        """Create the controlled container file inside the container."""
        subprocess.run(
            [
                "docker",
                "exec",
                self._name,
                "sh",
                "-c",
                "touch /tmp/controlled_container",
            ],
            check=True,
        )

    def _stop_container(self, name: str) -> bool:
        """Stop a container."""
        result = subprocess.run(
            ["docker", "stop", name], capture_output=True, text=True
        )
        return result.returncode == 0

    def _remove_container(self, name: str) -> bool:
        """Remove a container."""
        result = subprocess.run(["docker", "rm", name],
                                capture_output=True, text=True)
        return result.returncode == 0

    def _get_container_status(self, name: str) -> str:
        """Get the status of a container."""
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Status}}", name],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return "not found"
        return result.stdout.strip()
