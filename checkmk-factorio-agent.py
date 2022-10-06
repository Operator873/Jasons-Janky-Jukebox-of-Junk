#!/usr/bin/env python3

import os
import requests

# To determine your path, try a find command like:
# sudo find / -name "factorio" -type f 2>/dev/null
PATH="/opt/factorio/bin/x64/factorio --version"


def main():
    print("<<<factorio_version>>>")
    version = os.popen(PATH).readlines()[0]
    version_id = version.split(" ", 2)[1]

    avail = requests.get("https://factorio.com/api/latest-releases").json()

    try:
        avail_id = avail["stable"]["headless"]
    except (KeyError, ValueError):
        print("UNKNOWN No version returned by Factorio servers.")
        return

    if version_id == avail_id:
        print("OK Current version " + avail_id + " is installed.")
    else:
        print("CRITICAL Installed: " + version_id + " Avail: " + avail_id)


main()