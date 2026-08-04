#!/bin/sh

LOG_LEVEL="${LOG_LEVEL:-INFO}"
LOG_FILE="${LOG_FILE:-/tmp/logs}"

log_timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

log_format() {
  local level="$1"
  shift
  local msg="$*"
  echo "[$(log_timestamp)] [$level] $msg" | tee -a $LOG_FILE
}

log_debug() {
  [ "$LOG_LEVEL" = "DEBUG" ] || [ "$LOG_LEVEL" = "debug" ] || return 0
  log_format "DEBUG" "$*" >&2
}

log_info() {
  log_format "INFO" "$*" >&2
}

log_warn() {
  log_format "WARN" "$*" >&2
}

log_error() {
  log_format "ERROR" "$*" >&2
}

log_debug "log.sh loaded"
