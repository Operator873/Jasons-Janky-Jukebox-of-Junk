#!/usr/bin/env bash

# This script automates creating an ansible user, adding the pubkey for the user
# and finally adding an entry to /etc/sudoers.d for ansible
#
# Before using, be sure to export your pubkey as a variable called MYKEY like:
# export MYKEY=$(cat /home/ansible/id_rsa.pub)

if [ $UID -eq 0 ]; then
  # Check for running as root
  echo "This script must be run as a user with sudo privileges but not as root."
  exit 1
elif [ $# -eq 0 ]; then
  # Check a username was provided
  echo "Please provide desire ansible username. Example: ./this-script.sh ansible"
  exit 1
elif [ -x "${MYKEY}" ]; then
  # Check the pubkey was stored as a system variable
  echo "Please set your Ansible user's pubkey as a varibale called MYANSIBLEKEY."
  echo "Do this by executing: export MYANSIBLEKEY=\$(cat /home/yourAnsibleUser/.ssh/id_rsa.pub)}"
  exit 1
fi

# Create the user
sudo useradd -m -G wheel ${1}

# Check to make sure home directory was generated during the user create process
if [ ! -d "/home/${1}" ]; then
  echo "Unknown error occurred during home directory creation. Check logs..."
  exit 1
fi

# Start creating .ssh directory and echo pubkey into authorized_keys file.
# Set appropriate permissions and ownership
echo "$MYKEY" > /tmp/setup_tmpfile
sudo mkdir /home/${1}/.ssh
sudo mv /tmp/setup_tmpfile /home/${1}/.ssh/authorized_keys
sudo chmod 600 /home/${1}/.ssh/authorized_keys
sudo chmod 700 /home/${1}/.ssh
sudo chown -R ${1}:${1} /home/${1}/.ssh

echo "User ${1} sucessfully created and SSH key added."


echo "${1} ALL=(ALL) NOPASSWD:ALL" > /tmp/setup_sudoer
sudo chmod 644 /tmp/setup_sudoer
sudo chown root:root /tmp/setup_sudoer
sudo mv /tmp/setup_sudoer /etc/sudoers.d/${1}
echo "sudoers.d drop-in added."