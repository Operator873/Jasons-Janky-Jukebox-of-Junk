#!/usr/bin/env bash

# This script automates creating an ansible user, adding the pubkey for the user
# and finally adding an entry to /etc/sudoers.d for ansible
#
# Before using, be sure to export your pubkey as a variable call MYANSIBLEKEY like:
# export MYANSIBLEKEY=$(cat /home/ansible/id_rsa.pub)

if [ $UID -ne 0 ]; then
  # Check for running as root
  echo "This script must be run as root (sudo)"
  exit 1
elif [ $# -eq 0 ]; then
  # Check a username was provided
  echo "Please provide desire ansible username. Example: ./this-script.sh ansible"
  exit 1
elif [ -x ${MYANSIBLEKEY} ]; then
  # Check the pubkey was stored as a system variable
  echo "Please set your Ansible user's pubkey as a varibale called MYANSIBLEKEY."
  echo "Do this by executing: export MYANSIBLEKEY=\$(cat /home/yourAnsibleUser/.ssh/id_rsa.pub)}"
  exit 1
fi

# Create the user
useradd -m -G wheel ${1}

# Check to make sure home directory was generated during the user create process
if [ ! -d "/home/${1}" ]; then
  echo "Unknown error occurred during home directory creation. Check logs..."
  exit 1
fi

# Start creating .ssh directory and echo pubkey into authorized_keys file.
# Set appropriate permissions and ownership
cd /home/${1} || echo "Encountered error while changing to /home/${1}"; exit 1
mkdir .ssh
chmod 700 .ssh
cd .ssh || echo "Encountered error while changing to /home/${1}/.ssh"; exit 1
echo ${MYANSIBLEKEY} > authorized_keys
chmod 600 authorized_keys
cd /home/${1} || echo "Encountered error while changing to /home/${1}"; exit 1
chown -R ${1}:${1} .ssh

echo "User ${1} sucessfully created and SSH key added."