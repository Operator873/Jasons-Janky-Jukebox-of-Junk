#!/usr/bin/env bash

# This script automates creating an ansible service user, configuring its 
# authorized_keys file, and adding a validated passwordless sudoers entry.
#
# Usage: export MYANSIBLEKEY="ssh-rsa AAAAB3..."
#        ./bootstrap-ansible.sh <username>

set -euo pipefail

TARGET_USER="${1:-}"

# 1. Input Validation
if [ "$(id -u)" -eq 0 ]; then
  echo "[-] This script must be run via sudo, do not execute it directly as root."
  exit 1
fi

if [ -z "${TARGET_USER}" ]; then
  echo "[-] Missing target username. Example: ${0} ansible"
  exit 1
fi

if [ -z "${MYANSIBLEKEY:-}" ]; then
  echo "[-] Environment variable 'MYANSIBLEKEY' is empty or undefined."
  echo "    Execute: export MYANSIBLEKEY=\"\$(cat ~/.ssh/id_ed25519.pub)\""
  exit 1
fi

echo "[+] Bootstrapping configuration for user: ${TARGET_USER}"

# 2. Secure User Creation (Locked Password Account)
# -p '!' explicitly locks password authentication natively at creation
sudo useradd -m -G wheel -s /bin/bash -p '!' "${TARGET_USER}"

# Confirm home directory layout
HOME_DIR="/home/${TARGET_USER}"
if [ ! -d "${HOME_DIR}" ]; then
  echo "[-] Target home directory structure failed to generate."
  exit 1
fi

# 3. Secure Key Placement (Bypassing insecure world-readable /tmp)
# Create the directory first with absolute restricted mask states
sudo mkdir -p "${HOME_DIR}/.ssh"
sudo chmod 700 "${HOME_DIR}/.ssh"

# Stream key string directly into target without dropping intermediate temp files
echo "${MYANSIBLEKEY}" | sudo tee "${HOME_DIR}/.ssh/authorized_keys" > /dev/null
sudo chmod 600 "${HOME_DIR}/.ssh/authorized_keys"
sudo chown -R "${TARGET_USER}:${TARGET_USER}" "${HOME_DIR}/.ssh"

echo "[+] SSH Key mapping applied successfully."

# 4. Validated Sudoers Drop-in via Secure Root Temp Files
SUDO_TMP=$(mktemp /tmp/sudoer_setup.XXXXXX)
chmod 600 "${SUDO_TMP}"

echo "${TARGET_USER} ALL=(ALL) NOPASSWD:ALL" > "${SUDO_TMP}"

# Structural syntax validation check via visudo compilation engine
if sudo visudo -cf "${SUDO_TMP}" > /dev/null 2>&1; then
  sudo mv "${SUDO_TMP}" "/etc/sudoers.d/${TARGET_USER}"
  sudo chmod 0440 "/etc/sudoers.d/${TARGET_USER}"
  sudo chown root:root "/etc/sudoers.d/${TARGET_USER}"
  echo "[+] Validated sudoers drop-in applied."
else
  echo "[-] Sudoers syntax generation error encountered. Transaction aborted."
  rm -f "${SUDO_TMP}"
  exit 1
fi

echo "[+] System configuration successfully completed."