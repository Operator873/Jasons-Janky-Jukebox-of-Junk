#!/usr/bin/env python3

from tqdm import tqdm
import os
import sys
import json
import requests


def fetch_movie_ids(directory, apikey):
    # Gather up all files in the provided directory (this is recursive)
    print(f"Generating file list from {directory}")
    matches = []
    for _root, _dir, files in os.walk(directory):
        for f in tqdm(files):
            matches.append(f)

    # Take the files and split them up on a required file name format
    # Filename: 'The Movie Title (1999).mkv'
    print("Fetching TheMovieDB information...")
    inv = []
    for item in tqdm(matches):
        try:
            title, year = item.split(" (")
            year, _e = year.split(").")
            id = fetch_id(title, year, apikey)
            if id is None:
                print(f"{item} failed to produce a TMDB ID. Skipping...")
                continue

            inv.append(str(id))
        except Exception as err:
            # Fail with some noise... probably a badly formatted file name.
            print(f"{item} failed to split cleanly! Check file name format. {err}")
            continue

    return inv


def fetch_id(title, year, apikey):
    # Build a query for the MovieBot873 API to obtain the MovieDB ID
    query = {
        "query": "bot",
        "type": "movie",
        "title": title,
        "year": year,
        "apikey": apikey,
    }

    # Send the request to MovieBot873
    data = xmit(query, "get")

# Make sure we got something useful, and proceed.
    try:
        if data["success"] and len(data["results"]) > 1:
            dupes = []
            for item in data["results"]:
                if item["title"].lower() == title.lower() and item["year"] == year and not item["image"].endswith("None"):
                    dupes.append(item)

            if len(dupes) > 1:
                count = 1
                print("Multiple matches found!", file=sys.stdout)
                for dupe in dupes:
                    print(f"Option {count}: {dupe['invid']} - {dupe['title']} ({dupe['year']}) - {dupe['image']}")
                    count += 1
                choice = int(input("Which option is correct? ")) - 1
                result = dupes[choice]
            elif len(dupes) == 1:
                result = dupes[0]
            else:
                result = data["results"][0]
        elif data["success"] and len(data["results"]) == 1:
            result = data["results"][0]
        else:
            return None
    
    except Exception as e:
        print(f"Search for {title} failed! Dump follows: {str(e)} {data}")
        raise sys.exit(1)
    
    return result


def add_movie(inv, apikey):
    # Build a query to add the title to the database of owners.
    query = {
        "invid": inv["invid"],
        "add": "movie",
        "apikey": apikey,
    }

    # Send the data
    data = xmit(query, "post")

    return data["success"]


def xmit(query, method):
    # Set the API endpoint
    url = "https://873gear.com/moviebot"

    # Handle get requests for movie id info
    if method == "get":
        data = requests.get(url, params=query)

    # Handle post requests for adding movie to owner database
    if method == "post":
        data = requests.post(url, data="", params=query)

    # Make sure transaction was successful and return the obtain data
    if data.ok:
        return data.json()
    else:
        print(f"{data.json()}")


def main():
    counter = 0
    skipped = 0
    # Obtain some facts
    full_path = input("Enter full path to movies to add: ")
    apikey = input("Enter your API key: ")

    # Process items in the directory
    inventory = fetch_movie_ids(full_path, apikey)

    # Add the movies to MovieBot873
    print("Processing results and adding to MovieBot873...")
    for item in tqdm(inventory):
        if add_movie(item, apikey):
            counter += 1
        else:
            skipped += 1

    # Terminate with feedback
    print(f"Done! {counter} items added. {skipped} items were skipped due to failures.")


if __name__ == "__main__":
    main()
