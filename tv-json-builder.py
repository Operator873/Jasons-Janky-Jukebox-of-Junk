#!/bin/python3

import os
import re
import json


def main():
    print("HEADS UP! This script expects filebot style names like:")
    print("'Night Court - 1x01 - All You Need is Love.avi')")
    print("OR")
    print("Brooklyn Nine-Nine - S1E15 - Operation: Broken Feather.mkv")
    print("The '1x01'/'S1E01' format is matched for understanding season/episode/title\n")
    path_to_tv = input("Full path to folder containing ALL TV: ")
    # Or can be full path to outfile you desire
    owner = input("Owner name as will appear in Owner list: ")

    json_of_shows = process_list(process_dir(path_to_tv))

    with open(owner, 'w') as f:
        json.dump(json_of_shows, f, indent=2)


def process_dir(path):
    matches = []
    regex = r"([0-9]+x[0-9]+|S[0-9]+E[0-9]+)"

    for root, dir, files in os.walk(path):
        for f in files:
            if re.search(regex, f):
                matches.append(f)

    return matches


def process_list(all_shows):
    json_list_shows = {}

    for f in all_shows:
        try:
            name, info, title = f.split(' - ', 2)
        except ValueError:
            print(str(f) + " skipped due to missing ' - ' format.")
            continue

        if name in json_list_shows:
            json_list_shows[name][info] = title
        else:
            json_list_shows[name] = {info: title}

    return json_list_shows


if __name__ == "__main__":
    main()
