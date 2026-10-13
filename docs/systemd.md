# systemd deployment (Linux)

This guide installs the application under `/opt/gtfs-rt-filter`, keeps configuration under `/etc/gtfs-rt-filter`, and optionally exposes the command at `/usr/local/bin/gtfs-rt-filter`. The systemd unit runs the executable in the dedicated virtual environment directly.

## Quick Installation (recommended)

From the extracted project root, run:

```sh
./deploy.sh
```

The script prompts before installation and service activation. It requests
administrator privileges using `sudo` if needed. It performs the following
steps in order:

1. Checks Linux, systemd, and Python 3.11+.
2. Creates the `gtfsrtfilter` system account if it does not exist.
3. Copies the application to `/opt/gtfs-rt-filter` without copying a local `venv`.
4. Creates or reuses `/opt/gtfs-rt-filter/venv` and installs the package.
5. Creates `/etc/gtfs-rt-filter/config.yaml` from the example **only if missing**.
6. Installs the supplied systemd unit and reloads systemd.
7. Optionally creates the `/usr/local/bin/gtfs-rt-filter` command symlink.
8. Enables and starts (or restarts) the service, if confirmed.

For a noninteractive deployment accepting defaults:

```sh
./deploy.sh --yes
```

To also create the optional command symlink:

```sh
./deploy.sh --yes --link
```

**Important:** The script does not overwrite an existing configuration. On a
first install, edit `/etc/gtfs-rt-filter/config.yaml` to point at your actual
upstream feeds and restart the service afterward. The installer is intended
for trusted project sources. It installs Python dependencies using pip and
requires network access to your configured package index.

The script is safe to rerun for updates: it reuses the service account and
virtual environment, preserves configuration, refreshes the installed package,
and restarts the service if you approve. It does not delete files that are no
longer present in the new project version.

## Manual Installation (alternative)

### 1. Prerequisites

Install Python 3.11 or newer, its `venv` module, and `pip`. Run the commands below from the extracted project directory on a system using systemd. The example assumes the source tree has already been copied to `/opt/gtfs-rt-filter` (for example, using `sudo mkdir -p /opt/gtfs-rt-filter` and `sudo cp -a . /opt/gtfs-rt-filter/` from the project root).

### 2. Install the Application

```sh
cd /opt/gtfs-rt-filter
sudo python3 -m venv venv
sudo venv/bin/python -m pip install .
```

The installation is isolated in `/opt/gtfs-rt-filter/venv`. Do not install project files or a virtual environment directly into `/usr/local/bin`: that directory is intended for commands, not application trees.

To make the command available interactively from any directory, create an optional symlink:

```sh
sudo ln -s /opt/gtfs-rt-filter/venv/bin/gtfs-rt-filter /usr/local/bin/gtfs-rt-filter
```

The systemd service does not need this symlink.

### 3. Create a Service Account and Configuration

```sh
sudo useradd --system --no-create-home --shell /usr/sbin/nologin gtfsrtfilter
sudo mkdir -p /etc/gtfs-rt-filter

sudo cp /opt/gtfs-rt-filter/config.example.yaml /etc/gtfs-rt-filter/config.yaml
sudo chown root:root /etc/gtfs-rt-filter/config.yaml
sudo chmod 644 /etc/gtfs-rt-filter/config.yaml
```

If the service account already exists, skip `useradd`. Edit `/etc/gtfs-rt-filter/config.yaml` to configure real upstream URLs, paths and filters. If your configuration contains secrets, use more restrictive permissions and an appropriate group rather than mode `644`.

The service account must be able to traverse `/opt/gtfs-rt-filter` and read the virtual environment, YAML file, and any referenced GeoJSON files. The application files can remain owned by root; the service account does not need write access to them.

### 4. Register and Start the Service

```sh
sudo cp /opt/gtfs-rt-filter/deploy/gtfs-rt-filter.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gtfs-rt-filter
sudo systemctl status gtfs-rt-filter
```

The supplied unit assumes the paths and service account shown above. If you change any of them, edit the unit before enabling it.

## Logs and Maintenance

```sh
sudo journalctl -u gtfs-rt-filter -f
sudo systemctl restart gtfs-rt-filter
sudo systemctl stop gtfs-rt-filter
sudo systemctl start gtfs-rt-filter
```

Restart the service after changes to YAML or GeoJSON files, because configuration is loaded at startup. After modifying the **unit file**, also run `sudo systemctl daemon-reload` before restarting.

To update using the installer, run `./deploy.sh` from the new extracted project directory. Alternatively, after updating the source files in `/opt/gtfs-rt-filter`, run:

```sh
cd /opt/gtfs-rt-filter
sudo venv/bin/python -m pip install --upgrade .
sudo systemctl restart gtfs-rt-filter
```

## Disable or Remove the Service

```sh
sudo systemctl disable --now gtfs-rt-filter
sudo rm /etc/systemd/system/gtfs-rt-filter.service
sudo systemctl daemon-reload
```

If you created the optional symlink, remove it with `sudo rm /usr/local/bin/gtfs-rt-filter`. Remove application files, configuration, and the dedicated service account separately only if they are no longer needed.
