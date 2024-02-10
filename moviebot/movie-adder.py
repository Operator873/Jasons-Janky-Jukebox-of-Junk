#!/usr/bin/env python3

from tqdm import tqdm
import os
import requests


def main():
    # Obtain some facts
    full_path = input("Enter full path to movies to add: ")
    apikey = input("Enter your API key: ")

    # Process items in the directory
    inventory = fetch_movie_ids(full_path, apikey)

    # Add the movies to MovieBot873
    print("Processing results and adding to MovieBot873...")
    for item in tqdm(inventory):
        if item == "None":
            continue
        
        if add_movie(item, apikey):
            print(f"Successfully added {item}")

    # Terminate with feedback
    print("Done!")


def fetch_movie_ids(directory, apikey):
    # Gather up all files in the provided directory (this is recursive)
    print(f"Generating file list from {directory}")
    matches = []
    for root, dir, files in os.walk(directory):
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
            inv.append(str(fetch_id(title, year, apikey)))
        except:
            # Fail with some noise... probably a badly formatted file name.
            print(f"{item} failed!")
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
        if data["success"]:
            info = data["results"][0]
            return info.get("invid")
        else:
            print(f"{title} failed to add: {data}")
    except Exception as e:
        print(f"Search for {title} failed! Dump follows: {str(e)} {data}")


def add_movie(inv, apikey):
    # Build a query to add the title to the database of owners.
    query = {
        "invid": inv,
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


if __name__ == "__main__":
    main()
