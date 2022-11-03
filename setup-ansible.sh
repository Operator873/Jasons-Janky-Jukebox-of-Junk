#!/usr/bin/env bash

# This script automates creating an ansible user, adding the pubkey for the user
# and finally adding an entry to /etc/sudoers.d for ansible
#
# Before using, be sure to export your pubkey as a variable call MYANSIBLEKEY like:
# export MYANSIBLEKEY=$(cat /home/ansible/id_rsa.pub)

if [ $UID -ne 0 ]; then
  echo "This script must be run as root (sudo)"
  exit 1
elif [ $# -eq 0 ]; then
  echo "Please provide desire ansible username. Example: ./this-script.sh ansible"
  exit 1
elif [ -x ${MYANSIBLEKEY} ]; then
  echo "Please set your Ansible user's pubkey as a varibale called MYANSIBLEKEY."
  echo "Do this by executing: export MYANSIBLEKEY=\$(cat /home/yourAnsibleUser/.ssh/id_rsa.pub)}"
  exit 1
fi

useradd -m -G wheel ${1}
if [ -d "/home/${1}" ]; then
  cd /home/${1}
  mkdir .ssh
  chmod 700 .ssh
  cd .ssh
  echo ${MYANSIBLEKEY} > authorized_keys
  cd /home/${1}
  chown -R ${1}:${1} .ssh
else
  echo "Unknown error occurred during home directory creation. Check logs..."
fi
