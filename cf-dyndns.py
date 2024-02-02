#!/usr/bin/env python3

import CloudFlare
import requests
from datetime import datetime

# The CloudFlare library requires environment variables to be set with credentials
# CLOUDFLARE_API_KEY & CLOUDFLARE_EMAIL as a minimum
# use export CLOUDFLARE_EMAIL="youremail@address.com" or similar on your CLI
#
#
# Alternatively, you can pass the information directly to CloudFlare:
# cf = CloudFlare.CloudFlare(email="youremail@address.com", key="your global API key")


def get_public_ip():
    # Fetch current public IP address
    response = requests.get("https://api64.ipify.org?format=json").json()
    return response["ip"]


def check_records(cf, records, current_ip):
    # For each DNS record in a zone, check the IP and update if necessary
    for record in records:

        if current_ip == record["content"]:
            print(f"{record['name']} currently has correct IP. Skipping...")
            continue
        elif record['type'] != "A":
            continue
        else:
            data = {
                "content": current_ip,
                "proxied": False,
                "name": record["name"],
                "type": "A",
                "ttl": 60,
                "comment": f"Updated via script at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            }

            cf.zones.dns_records.put(record["zone_id"], record["id"], data=data)
            print(
                f"Update successful! {record['name']} was updated to IP: {current_ip}"
            )


def main():
    cf = CloudFlare.CloudFlare()
    ipv4 = get_public_ip()

    # Pull all zones and send to record check
    for site in cf.zones.get():
        records = cf.zones.dns_records.get(site["id"])
        if not records:
            print(f"Error! DNS record for {site['name']} not found!")
            continue

        check_records(cf, records, ipv4)


if __name__ == "__main__":
    main()
