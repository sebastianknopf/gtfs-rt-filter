#!/usr/bin/env bash
# Remove the gtfs-rt-filter systemd installation and optionally its data/account.
set -Eeuo pipefail

APP_NAME=gtfs-rt-filter
SERVICE_USER=gtfsrtfilter
APP_DIR=/opt/gtfs-rt-filter
CONFIG_DIR=/etc/gtfs-rt-filter
UNIT_FILE=/etc/systemd/system/gtfs-rt-filter.service
BIN_LINK=/usr/local/bin/gtfs-rt-filter
MANAGED_LINK_TARGET="$APP_DIR/venv/bin/gtfs-rt-filter"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ASSUME_YES=false
PURGE=false

usage() {
  cat <<'HELP'
Usage: ./uninstall.sh [--yes] [--purge] [--help]

  --yes    Remove installed service, application, and managed command symlink
           without prompting. Keep configuration and system account.
  --purge  Also remove /etc/gtfs-rt-filter and the gtfsrtfilter account.
           Intended for complete removal; requires --yes for unattended use.
  --help   Show this help.

Interactive mode asks separately before removing the service, symlink,
application, configuration, and system account.
HELP
}

for arg in "$@"; do
  case "$arg" in
    --yes) ASSUME_YES=true ;;
    --purge) PURGE=true ;;
    --help|-h) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$arg" >&2; usage >&2; exit 2 ;;
  esac
done

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
log() { printf '\n==> %s\n' "$*"; }
confirm() {
  local question="$1" default="${2:-yes}" answer
  if "$ASSUME_YES"; then
    [[ "$default" == yes ]] || "$PURGE"
    return $?
  fi
  [[ -t 0 ]] || fail 'No interactive input. Use --yes (and optionally --purge).'
  if [[ "$default" == yes ]]; then
    read -r -p "$question [Y/n] " answer
    [[ -z "$answer" || "$answer" =~ ^[Yy]([Ee][Ss])?$ ]]
  else
    read -r -p "$question [y/N] " answer
    [[ "$answer" =~ ^[Yy]([Ee][Ss])?$ ]]
  fi
}

[[ "$(uname -s)" == Linux ]] || fail 'Linux is required.'
command -v systemctl >/dev/null || fail 'systemd is required.'
if (( EUID != 0 )); then
  command -v sudo >/dev/null || fail 'Run as root or install sudo.'
  exec sudo -- "$SCRIPT_DIR/uninstall.sh" "$@"
fi

printf 'Uninstall %s\n  Application: %s\n  Config: %s\n  Unit: %s\n' \
  "$APP_NAME" "$APP_DIR" "$CONFIG_DIR" "$UNIT_FILE"
confirm 'Proceed with uninstallation?' || { echo 'Cancelled.'; exit 0; }

if [[ -f "$UNIT_FILE" ]]; then
  if confirm 'Stop, disable, and remove the systemd service?'; then
    log 'Removing systemd service'
    systemctl stop "$APP_NAME.service" || fail 'Could not stop the service; refusing to continue.'
    systemctl disable "$APP_NAME.service" || fail 'Could not disable the service.'
    rm -f -- "$UNIT_FILE"
    systemctl daemon-reload
    systemctl reset-failed "$APP_NAME.service" 2>/dev/null || true
  else
    fail 'Service was retained; aborting to avoid removing files used by a running service.'
  fi
elif systemctl is-active --quiet "$APP_NAME.service"; then
  fail 'A service with this name is running without the expected unit file; aborting.'
fi

if [[ -L "$BIN_LINK" && "$(readlink -- "$BIN_LINK")" == "$MANAGED_LINK_TARGET" ]]; then
  if confirm "Remove managed symlink $BIN_LINK?"; then
    rm -- "$BIN_LINK"
  fi
elif [[ -e "$BIN_LINK" || -L "$BIN_LINK" ]]; then
  echo "Leaving unrelated path untouched: $BIN_LINK"
fi

if [[ -d "$APP_DIR" ]] && confirm "Delete application and venv under $APP_DIR?"; then
  log 'Removing application directory'
  rm -rf -- "$APP_DIR"
fi

if [[ -d "$CONFIG_DIR" ]] && confirm "Delete configuration directory $CONFIG_DIR (data loss)?" no; then
  log 'Removing configuration directory'
  rm -rf -- "$CONFIG_DIR"
else
  echo "Preserving configuration: $CONFIG_DIR"
fi

if getent passwd "$SERVICE_USER" >/dev/null && confirm "Delete system account $SERVICE_USER?" no; then
  if pgrep -u "$SERVICE_USER" >/dev/null 2>&1; then
    echo "Keeping account: processes are still running as $SERVICE_USER" >&2
  else
    command -v userdel >/dev/null || fail 'userdel is required to remove the account.'
    userdel "$SERVICE_USER"
    # Remove the private group only when it has no members and no other user
    # has it as their primary group.
    if getent group "$SERVICE_USER" >/dev/null && command -v groupdel >/dev/null; then
      gid="$(getent group "$SERVICE_USER" | cut -d: -f3)"
      if ! getent passwd | awk -F: -v gid="$gid" '$4 == gid { found=1 } END { exit !found }'; then
        groupdel "$SERVICE_USER" || echo "Keeping group: $SERVICE_USER" >&2
      fi
    fi
    echo "Removed system account: $SERVICE_USER"
  fi
else
  echo "Preserving system account: $SERVICE_USER"
fi

log 'Uninstallation finished'
