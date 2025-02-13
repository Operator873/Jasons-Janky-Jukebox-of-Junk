#!/usr/bin/env python3

import json
import os

from tqdm import tqdm


def process_dir(path):
    print("Gathering files...")
    matches = []

    for _root, _dir, files in os.walk(path):
        for f in tqdm(files):
            matches.append(f)

    return matches


def process_list(movies):
    print(f"Building JSON list")
    build_list = []

    for m in tqdm(movies):
        try:
            title, year = m.split(" (")
            year, _filetype = year.split(").")
        except ValueError:
            print(m + " failed to split cleanly! Skipping...")
            continue

        entry = {"title": title, "year": year}
        build_list.append(entry)

    return build_list


def main():
    movies = input("Full path to movies: ")
    # Or the full path of the outfile you desire if not the owner name
    owner = input("Owner name (filename): ")

    with open(owner, "w") as f:
        json.dump(process_list(process_dir(movies)), f, indent=2)


if __name__ == "__main__":
    main()
