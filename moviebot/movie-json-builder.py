#!/usr/bin/env python3

import os
import json


def main():
    movies = input("Full path to movies: ")
    # Or the full path of the outfile you desire if not the owner name
    owner = input("Owner name: ")

    with open(owner, 'w') as f:
        json.dump(process_list(process_dir(movies)), f, indent=2)


def process_dir(path):
    matches = []

    for root, dir, files in os.walk(path):
        for f in files:
            matches.append(f)

    return matches


def process_list(movies):
    build_list = []

    for m in movies:
        try:
            title, year = m.split(" (")
            year, _filetype = year.split(").")
        except ValueError:
            print(m + " failed!")
            continue

        entry = {"title": title, "year": year}
        build_list.append(entry)

    return build_list


if __name__ == "__main__":
    main()