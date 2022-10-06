#!/bin/python3

import requests
from datetime import datetime as right


def xmit(ip, payload):
    apiurl = "https://domains.google.com/nic/update"
    domain, user, pword = payload
    url = "https://" + user + ":" + pword + "@domains.google.com/nic/update?hostname=" + domain + "&myip=" + ip
    headers = {
        "User-Agent": "Python3 requests library for 873gear.com"
    }
    x = requests.post(url, headers=headers)

    if 'nochg' not in str(x.text):
        with open('dyndnslog.txt', 'a') as f:
            f.write(str(right.now()) + " >> " + str(x.reason) + " || " + str(x.status_code) + " || " + str(x.text) + "\n")


def main():
    currentip = requests.get(url="https://domains.google.com/checkip").text
    my_site = ("domain", "key", "value")
    my_other_site = ("domain", "key", "value")
    list = [my_site, my_other_site]

    for item in list:
        xmit(currentip, item)

if __name__ == "__main__":
    main()
