# systemd deployment (Linux)

This guide installs the application under `/opt/gtfs-rt-filter`, keeps configuration under `/etc/gtfs-rt-filter`, and optionally exposes the command at `/usr/local/bin/gtfs-rt-filter`. The systemd unit runs the executable in the dedicated virtual environment directly.

## Quick Installation (recommended)

Clone the repository including its `.git` directory (a GitHub-generated source
archive is **not sufficient**). For example:

```sh
git clone https://github.com/sebastianknopf/gtfs-rt-filter.git
cd gtfs-rt-filter
```

From the checked-out project root, run:

```sh
./install.sh
```

The script prompts separately for service unit installation, enabling at boot, and starting/restarting. It requests
administrator privileges using `sudo` if needed. It performs the following
steps in order:

1. Checks Linux, systemd, Git metadata, and Python 3.11+.
2. Creates the `gtfsrtfilter` system account if it does not exist.
3. Copies the application **including `.git`** to `/opt/gtfs-rt-filter`, without copying a local `venv`.
4. Creates or reuses `/opt/gtfs-rt-filter/venv` and installs the package.
5. Creates `/etc/gtfs-rt-filter/config.yaml` from the example **only if missing**.
6. Installs the supplied systemd unit and reloads systemd.
7. Optionally creates the `/usr/local/bin/gtfs-rt-filter` command symlink.
8. Separately asks whether to enable the service at boot.
9. Separately asks whether to start/restart the service now.

For a noninteractive deployment accepting defaults:

```sh
./install.sh --yes
```

To install without registering a systemd service:

```sh
./install.sh --no-service
```

To install the service but leave it disabled and stopped:

```sh
./install.sh --yes --no-enable --no-start
```

To also create the optional command symlink:

```sh
./install.sh --yes --link
```

**Important:** The script does not overwrite an existing configuration. On a
first install, edit `/etc/gtfs-rt-filter/config.yaml` to point at your actual
upstream feeds and restart the service afterward. The installer is intended
for trusted project sources. It installs Python dependencies using pip and
requires network access to your configured package index.

The script requires a full Git checkout; it replaces the deployed `.git` directory with the checkout metadata on each update. Do not edit or commit directly in `/opt/gtfs-rt-filter`.

The script is safe to rerun for updates: it reuses the service account and
virtual environment, preserves configuration, refreshes the installed package,
and restarts the service if you approve. It does not delete files that are no
longer present in the new project version.

## Manual Installation (alternative)

### 1. Prerequisites

Install Python 3.11 or newer, its `venv` module, `pip`, and Git. Run the commands below from the extracted project directory on a system using systemd. The example assumes a complete Git checkout, including `.git`, has already been copied to `/opt/gtfs-rt-filter` (for example, using `sudo mkdir -p /opt/gtfs-rt-filter` and `sudo cp -a . /opt/gtfs-rt-filter/` from the project root).

### 2. Install the Application

```sh
cd /opt/gtfs-rt-filter
sudo python3 -m venv venv
sudo venv/bin/python -m pip install .
# setuptools-scm reads the local .git directory and writes version.py
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

To update using the installer, run `./install.sh` from the new extracted project directory. Alternatively, after updating the source files in `/opt/gtfs-rt-filter`, run:

```sh
cd /opt/gtfs-rt-filter
sudo venv/bin/python -m pip install --upgrade .
sudo systemctl restart gtfs-rt-filter
```

## Uninstallation

From the project checkout, run:

```sh
./uninstall.sh
```

The uninstaller separately asks to stop/disable and remove the systemd unit,
remove the managed `/usr/local/bin/gtfs-rt-filter` symlink, remove the
application directory, remove the configuration directory, and delete the
`gtfsrtfilter` system account. It preserves configuration and the account by
default in noninteractive mode. **Review the prompts carefully:** removing the
application directory also removes its deployed Git checkout and virtual
environment. The original source checkout is not touched.

For unattended removal of the service, application and managed symlink while
preserving configuration and account:

```sh
./uninstall.sh --yes
```

To remove configuration and the service account as well:

```sh
./uninstall.sh --yes --purge
```

The uninstaller does not remove unrelated files or a preexisting symlink with a
different target. It does not delete a service account that is still in use by
running processes.

## Disable or Remove the Service

```sh
sudo systemctl disable --now gtfs-rt-filter
sudo rm /etc/systemd/system/gtfs-rt-filter.service
sudo systemctl daemon-reload
```

If you created the optional symlink, remove it with `sudo rm /usr/local/bin/gtfs-rt-filter`. Remove application files, configuration, and the dedicated service account separately only if they are no longer needed.
