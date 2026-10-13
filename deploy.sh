#!/usr/bin/env bash
# Interactive systemd installer/updater for gtfs-rt-filter.
set -Eeuo pipefail

APP_NAME=gtfs-rt-filter
SERVICE_USER=gtfsrtfilter
APP_DIR=/opt/gtfs-rt-filter
CONFIG_DIR=/etc/gtfs-rt-filter
CONFIG_FILE="$CONFIG_DIR/config.yaml"
UNIT_FILE=/etc/systemd/system/gtfs-rt-filter.service
BIN_LINK=/usr/local/bin/gtfs-rt-filter
SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ASSUME_YES=false
INSTALL_LINK=false

usage() {
  cat <<'HELP'
Usage: ./deploy.sh [--yes] [--link] [--help]

Install or update gtfs-rt-filter for systemd on Linux.
  --yes    Accept defaults without prompting (does not overwrite config).
  --link   Create /usr/local/bin/gtfs-rt-filter symlink.
  --help   Display this help.

A complete Git checkout (including .git) is required for setuptools-scm.

Run from the extracted project directory. The script asks for sudo/root
privileges, installs the project under /opt/gtfs-rt-filter, and enables
and starts the systemd service. Existing configuration is preserved.
HELP
}

for arg in "$@"; do
  case "$arg" in
    --yes) ASSUME_YES=true ;;
    --link) INSTALL_LINK=true ;;
    --help|-h) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$arg" >&2; usage >&2; exit 2 ;;
  esac
done

log() { printf '\n==> %s\n' "$*"; }
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
confirm() {
  local question="$1" answer
  if "$ASSUME_YES"; then return 0; fi
  if [[ ! -t 0 ]]; then fail 'Interactive input unavailable. Use --yes to accept defaults.'; fi
  read -r -p "$question [Y/n] " answer
  [[ -z "$answer" || "$answer" =~ ^[Yy]([Ee][Ss])?$ ]]
}

[[ "$(uname -s)" == Linux ]] || fail 'Linux is required.'
command -v systemctl >/dev/null || fail 'systemd (systemctl) is required.'
command -v python3 >/dev/null || fail 'python3 is required.'
[[ -f "$SOURCE_DIR/pyproject.toml" && -f "$SOURCE_DIR/deploy/gtfs-rt-filter.service" ]] || fail 'Run deploy.sh from the complete project distribution.'
[[ -d "$SOURCE_DIR/.git" ]] || fail 'A complete Git checkout with a .git directory is required. Deploy from a git clone, not a source ZIP.'
command -v git >/dev/null || fail 'git is required to determine the package version.'
git -C "$SOURCE_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail 'The source directory must be a valid Git checkout.' 
python3 - <<'PY' || fail 'Python 3.11 or newer is required.'
import sys
assert sys.version_info >= (3, 11)
PY

if (( EUID != 0 )); then
  command -v sudo >/dev/null || fail 'Run as root or install sudo.'
  log 'Requesting administrator privileges'
  exec sudo -- "$SOURCE_DIR/deploy.sh" "$@"
fi

printf 'Deploy %s\n  Source: %s\n  Application: %s\n  Configuration: %s\n  Unit: %s\n' \
  "$APP_NAME" "$SOURCE_DIR" "$APP_DIR" "$CONFIG_FILE" "$UNIT_FILE"
confirm 'Proceed with installation/update?' || { echo 'Cancelled.'; exit 0; }

log 'Creating the dedicated system account (if missing)'
if ! getent passwd "$SERVICE_USER" >/dev/null; then
  command -v useradd >/dev/null || fail 'useradd is required.'
  useradd --system --no-create-home --shell /usr/sbin/nologin "$SERVICE_USER"
fi
getent group "$SERVICE_USER" >/dev/null || fail "Required group $SERVICE_USER is missing."

log 'Copying application files'
mkdir -p "$APP_DIR" "$CONFIG_DIR"
# Avoid copying a virtual environment or developer files. Preserve an existing
# installation's venv and any local files in /opt.
if [[ "$SOURCE_DIR" != "$APP_DIR" ]]; then
  for entry in pyproject.toml README.md LICENSE.md config.example.yaml .gitignore; do
    [[ ! -f "$SOURCE_DIR/$entry" ]] || install -m 644 "$SOURCE_DIR/$entry" "$APP_DIR/$entry"
  done
  for directory in src docs deploy tests .github; do
    if [[ -d "$SOURCE_DIR/$directory" ]]; then
      mkdir -p "$APP_DIR/$directory"
      cp -a "$SOURCE_DIR/$directory/." "$APP_DIR/$directory/"
    fi
  done
  # setuptools-scm needs Git metadata to derive the version during pip install.
  # Replace the previous Git metadata rather than merging potentially stale refs.
  rm -rf -- "$APP_DIR/.git"
  cp -a -- "$SOURCE_DIR/.git" "$APP_DIR/.git"
  install -m 755 "$SOURCE_DIR/deploy.sh" "$APP_DIR/deploy.sh"
fi
# All application code must be readable by the unprivileged service account.
chmod 755 "$APP_DIR"

log 'Preparing virtual environment and installing dependencies'
if [[ ! -x "$APP_DIR/venv/bin/python" ]]; then
  python3 -m venv "$APP_DIR/venv" || fail 'Could not create venv. Install your distribution python3-venv package.'
fi
# Use the project directory as the build context so setuptools-scm sees .git.
"$APP_DIR/venv/bin/python" -m pip install --upgrade "$APP_DIR"

log 'Preparing configuration'
if [[ -e "$CONFIG_FILE" ]]; then
  echo "Preserving existing configuration: $CONFIG_FILE"
else
  install -m 644 "$APP_DIR/config.example.yaml" "$CONFIG_FILE"
  echo "Created example configuration: $CONFIG_FILE"
  echo 'IMPORTANT: Edit upstream URLs and filters before using the service.'
fi
chmod 755 "$CONFIG_DIR"
# Do not loosen permissions on an existing config, which may contain secrets.

log 'Installing systemd unit'
install -m 644 "$APP_DIR/deploy/gtfs-rt-filter.service" "$UNIT_FILE"
systemctl daemon-reload

if "$INSTALL_LINK" || { ! "$ASSUME_YES" && confirm "Create optional command symlink at $BIN_LINK?"; }; then
  if [[ -L "$BIN_LINK" && "$(readlink "$BIN_LINK")" == "$APP_DIR/venv/bin/gtfs-rt-filter" ]]; then
    echo 'Command symlink already exists.'
  elif [[ -e "$BIN_LINK" || -L "$BIN_LINK" ]]; then
    echo "Skipping symlink: $BIN_LINK already exists and is not managed by this script."
  else
    ln -s "$APP_DIR/venv/bin/gtfs-rt-filter" "$BIN_LINK"
  fi
fi

if confirm 'Enable and start/restart the systemd service now?'; then
  systemctl enable "$APP_NAME.service"
  systemctl restart "$APP_NAME.service"
  systemctl --no-pager --full status "$APP_NAME.service" || true
else
  echo "Service installed but not started. Run: systemctl enable --now $APP_NAME"
fi

log 'Deployment finished'
printf 'Config: %s\nLogs: journalctl -u %s -f\n' "$CONFIG_FILE" "$APP_NAME"
