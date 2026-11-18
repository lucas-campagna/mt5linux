"""MT5 configuration using Pydantic Settings.

Automatic environment variable loading with MT5_ prefix.
Single source of truth for all configuration across the project.

Hierarchy Level: 1
- Imports: MT5Constants (Level 0)
- Used by: MT5Models, MT5Utilities, client.py, bridge.py, conftest.py

Configuration Sources (precedence high to low):
1. Environment variables (MT5_*)
2. .env file
3. Defaults defined here

Usage:
    >>> from mt5linux.settings import MT5Settings
    >>> config = MT5Settings()  # loads from env
    >>> print(config.grpc_port)  # 8001 or env override
    >>> delay = config.calculate_retry_delay(attempt=2)
"""

import random

from pydantic_settings import BaseSettings, SettingsConfigDict

from mt5linux.grpc_constants import MT5Constants


class MT5Settings(BaseSettings):
    """MetaTrader5 configuration with automatic env loading.

    Single source of truth for all MT5 configuration across the project.
    All fields auto-load from environment variables with MT5_ prefix.

    Port Configuration Strategy:
    - grpc_port/vnc_port/health_port: Container INTERNAL ports (8001/3000/8002)
    - docker_*_port: Host-mapped ports for direct Docker access (38812/33000/38002)
    - test_*_port: Isolated ports for pytest (28812/23000/28002)

    Usage:
        config = MT5Settings()  # loads from env
        config = MT5Settings(host="custom")  # override
    """

    model_config = SettingsConfigDict(
        env_prefix="MT5_",
        frozen=True,
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # =========================================================================
    # NETWORK - Production (Container Internal Ports)
    # =========================================================================
    host: str = "localhost"
    grpc_port: int = 8001  # Container internal gRPC port
    bridge_port: int = 8001  # Alias for grpc_port (legacy)
    vnc_port: int = 3000  # Container internal VNC port
    health_port: int = 8002  # Container internal health port

    # =========================================================================
    # DOCKER - Host-Mapped Ports (for direct Docker access)
    # =========================================================================
    docker_grpc_port: int = 38812  # Host port mapped to container 8001
    docker_vnc_port: int = 33000  # Host port mapped to container 3000
    docker_health_port: int = 38002  # Host port mapped to container 8002

    # =========================================================================
    # TEST ENVIRONMENT - Isolated Ports (avoid conflicts with other projects)
    # =========================================================================
    # Isolated from: production (8001), neptor (18812), mt5docker (48812)
    test_grpc_port: int = 28812  # Isolated test gRPC port
    test_vnc_port: int = 23000  # Isolated test VNC port
    test_health_port: int = 28002  # Isolated test health port
    test_container_name: str = "mt5linux-test"  # Isolated container name
    test_startup_timeout: int = 420  # Container startup timeout (7 min)
    test_grpc_timeout: int = 60  # gRPC health check timeout

    # =========================================================================
    # TIMEOUTS (in seconds)
    # =========================================================================
    timeout_connection: int = 300
    timeout_health_check: int = 60
    startup_health_timeout: float = 30.0  # Health check during startup
    connection_cooldown: float = 0.1  # Cooldown after disconnect

    # =========================================================================
    # RETRY SETTINGS
    # =========================================================================
    retry_max_attempts: int = 3
    retry_initial_delay: float = 0.5
    retry_max_delay: float = 10.0
    retry_exponential_base: float = 2.0
    retry_jitter: bool = True
    retry_min_interval: float = 0.5  # Min backoff interval for startup
    retry_max_interval: float = 5.0  # Max backoff interval for startup

    # =========================================================================
    # CIRCUIT BREAKER
    # =========================================================================
    cb_threshold: int = 5
    cb_recovery: float = 30.0
    cb_half_open_max: int = 3

    # =========================================================================
    # TRANSACTION HANDLING (for CRITICAL operations like order_send)
    # =========================================================================
    tx_log_critical: bool = True
    """Log TX_INTENT/TX_RESULT for CRITICAL operations (order_send)."""

    tx_verify_timeout: float = 5.0
    """Timeout in seconds for state verification after ambiguous errors."""

    tx_verify_on_ambiguous: bool = True
    """Verify order state when receiving CONDITIONAL/UNKNOWN retcodes."""

    tx_verify_max_attempts: int = 3
    """Max verification attempts after ambiguous response (TIMEOUT/CONNECTION)."""

    tx_verify_propagation_delay: float = 0.5
    """Delay in seconds for MT5 internal sync before/between verifications."""

    tx_verify_search_window_minutes: int = 15
    """Time window in minutes for comment-based deal verification."""

    critical_retry_max_attempts: int = 5
    """Max retry attempts for CRITICAL operations (more than standard)."""

    critical_retry_initial_delay: float = 0.1
    """Initial retry delay for CRITICAL ops (faster than standard)."""

    critical_retry_max_delay: float | None = None
    """Max delay for CRITICAL retries. If None, uses retry_max_delay/2."""

    # =========================================================================
    # RESILIENCE FEATURE FLAGS (enabled by default for production reliability)
    # =========================================================================
    enable_auto_reconnect: bool = True
    """Enable automatic reconnection with exponential backoff."""

    enable_health_monitor: bool = True
    """Enable background health monitoring task."""

    enable_circuit_breaker: bool = True
    """Enable circuit breaker pattern for cascading failure prevention."""

    # =========================================================================
    # REQUEST QUEUE - PARALLEL EXECUTION
    # =========================================================================
    queue_max_concurrent: int = 10
    """Max SIMULTANEOUS operations executing in parallel (match server workers)."""

    queue_max_depth: int = 1000
    """Max pending requests before backpressure (raises QueueFullError)."""

    # =========================================================================
    # WRITE-AHEAD LOG (WAL) - ORDER PERSISTENCE
    # =========================================================================
    wal_path: str = "~/.mt5linux/wal.db"
    """Path to WAL SQLite database for order persistence."""

    wal_retention_days: int = 7
    """Auto-cleanup verified/failed WAL entries older than this."""

    # =========================================================================
    # SERVER (bridge.py)
    # =========================================================================
    server_host: str = "0.0.0.0"  # Server bind address
    server_port: int = 8001  # Server listen port (aligned with grpc_port)
    server_grace_period: int = 5  # Graceful shutdown timeout
    thread_pool_size: int = 10
    max_restarts: int = 10
    restart_delay_base: float = 1.0
    restart_delay_max: float = 60.0
    restart_delay_multiplier: float = 2.0
    jitter_factor: float = 0.1

    # =========================================================================
    # gRPC PROTOCOL
    # =========================================================================
    grpc_max_message_size: int = 50 * 1024 * 1024  # 50MB
    grpc_keepalive_time_ms: int = 30000  # 30 seconds
    grpc_keepalive_timeout_ms: int = 10000  # 10 seconds

    # =========================================================================
    # ORDER DEFAULTS (from MT5Constants)
    # =========================================================================
    order_filling: int = MT5Constants.Order.OrderFilling.FOK
    order_time: int = MT5Constants.Order.OrderTime.GTC
    order_deviation: int = 20
    order_magic: int = 0

    # =========================================================================
    # CALCULATION METHODS
    # =========================================================================

    def calculate_retry_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with optional jitter.

        Args:
            attempt: Current attempt number (0-indexed).

        Returns:
            Delay in seconds before next retry.

        """
        delay = min(
            self.retry_initial_delay * (self.retry_exponential_base**attempt),
            self.retry_max_delay,
        )
        if self.retry_jitter:
            # Add 0-100% jitter (random is fine for jitter)
            delay *= 0.5 + random.random()
        return delay

    def calculate_backoff_delay(self, attempt: int) -> float:
        """Calculate server restart backoff delay with jitter.

        Args:
            attempt: Current attempt number (0-indexed).

        Returns:
            Delay in seconds with jitter applied.

        """
        delay = self.restart_delay_base * (self.restart_delay_multiplier**attempt)
        delay = min(delay, self.restart_delay_max)
        # random is fine for jitter - not cryptographic
        jitter = delay * self.jitter_factor * (2 * random.random() - 1)
        return max(0, delay + jitter)

    def calculate_critical_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay for CRITICAL operations (faster).

        Uses critical_retry_initial_delay (0.1s default) instead of
        retry_initial_delay (0.5s default) for faster retry on
        CRITICAL trading operations like order_send.

        The shorter delay is appropriate because:
        1. CRITICAL operations need faster recovery
        2. We've already verified state, so retry is safe
        3. Market conditions may change quickly

        Args:
            attempt: Current attempt number (0-indexed).

        Returns:
            Delay in seconds before next retry (shorter than standard).

        """
        # Use explicit max_delay if set, otherwise half of normal max
        max_delay = (
            self.critical_retry_max_delay
            if self.critical_retry_max_delay is not None
            else self.retry_max_delay / 2
        )
        delay = min(
            self.critical_retry_initial_delay * (self.retry_exponential_base**attempt),
            max_delay,
        )
        if self.retry_jitter:
            # Add 0-100% jitter (random is fine for jitter)
            delay *= 0.5 + random.random()
        return delay

    def get_grpc_channel_options(self) -> list[tuple[str, int]]:
        """Get gRPC channel options from configuration.

        Returns:
            List of (option_name, value) tuples for gRPC channel creation.

        """
        return [
            ("grpc.max_send_message_length", self.grpc_max_message_size),
            ("grpc.max_receive_message_length", self.grpc_max_message_size),
            ("grpc.keepalive_time_ms", self.grpc_keepalive_time_ms),
            ("grpc.keepalive_timeout_ms", self.grpc_keepalive_timeout_ms),
        ]
