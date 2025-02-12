#!/usr/bin/env python3

import os
import sys

import mysql.connector
import requests
from tqdm import tqdm

# MySQL/MariaDB config
HOST = "xxx.xxx.xxx.xxx"  # The IP of your database. "localhost" is also acceptable
USER = "myCoolUser"  # The username to connect to the database with
PASSWD = "123abc"  # The password for the above user
DBASE = "Plex"  # The name of the database in MySQL/MariaDB to use
TABLE = "Movies"  # The name of the table within the database to use

# Unattended. Set to True to handle duplicate matching
AUTO = False

# 873gear API key
APIKEY = None  # Replace with your API key for automated runs. (str)

# Movie Directory
PATH = (
    None  # Replace with Fully Qualified Path to your movies for automated runs. (str)
)


def connect_to_mysql():
    try:
        mydb = mysql.connector.connect(
            host=HOST, user=USER, password=PASSWD, database=DBASE
        )
        print("Database Connection successful!")
        return mydb
    except mysql.connector.Error as e:
        if e.errno == 2003:
            print("Connection timed out or server not found.")
        else:
            print(f"Connection error: {e}")
        return None


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
                print(
                    f"{item} failed to produce a TMDB ID. Skipping...", file=sys.stdout
                )
                continue

            inv.append(str(id))

        except:
            # Fail with some noise... probably a badly formatted file name.
            print(
                f"{item} failed to split cleanly! Check file name format.",
                file=sys.stdout,
            )
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
    data = xmit(query)

    # Make sure we got something useful, and proceed.
    try:
        dupes = []
        if data["success"] and len(data["results"]) > 1:
            if AUTO:
                return None

            for item in data.get("results"):
                if item["title"].lower() == title.lower() and item["year"] == year:
                    dupes.append(item)

                if len(dupes) > 1:
                    count = 1
                    print("Multiple matches found!", file=sys.stdout)
                    for dupe in dupes:
                        print(
                            f"Option {count}: {dupe['invid']} - {dupe['title']} ({dupe['year']}) - {dupe['image']}",
                            file=sys.stdout,
                        )
                        count += 1
                    choice = int(input("Which option is correct? ")) - 1
                    info = dupes[choice]
                else:
                    info = dupes[0]
        else:
            info = data["results"][0]

        return info.get("invid")

    except Exception as e:
        print(f"Search for {title} failed! Dump follows: {str(e)} {data}")
        raise SystemExit(1)


def add_movie(db, inv, apikey):
    c = db.cursor()
    check = f"SELECT tmdbID FROM {TABLE} WHERE tmdbID = %s"
    insert = f"INSERT INTO {TABLE} (tmdbID, movieTitle, movieImage, movieYear, movieGenre, movieDescription) VALUES (%s, %s, %s, %s, %s, %s)"

    c.execute(check, (inv,))
    exists = c.fetchone()

    if not exists:
        query = {
            "query": "bot",
            "type": "movie",
            "invid": inv,
        }

        data = xmit(query)
        info = data["results"][0]
        values = (
            info["invid"],
            info["title"],
            info["image"],
            int(info["year"]),
            info["genres"],
            info["overview"],
        )
        try:
            c.execute(insert, values)
            db.commit()
        except mysql.connector.Error as e:
            db.rollback()
            print(f"MySQL Error: {e}", file=sys.stdout)

    # Build a query to add the title to the 873gear database of owners.
    query = {
        "invid": inv,
        "add": "movie",
        "apikey": apikey,
    }

    # Send the data
    data = xmit(query, "post")

    return data["success"]


def xmit(query, method="get"):
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


def check_table(db):
    c = db.cursor()
    try:
        c.execute(f"SELECT * FROM {TABLE} LIMIT 1")

    except mysql.connector.Error as err:
        if err.errno == 1146:
            print(f"Movies database table '{TABLE}' not found! Creating in {DBASE}...")
            create_table = f"""
            CREATE TABLE {TABLE} (
                tmdbID INT PRIMARY KEY,
                movieTitle VARCHAR(255) NOT NULL,
                movieImage VARCHAR(255),
                movieYear YEAR(4),
                movieGenre VARCHAR(255),
                movieDescription TEXT
            )
            """
            try:
                c.execute(create_table)
                db.commit()
                print("Movies table created!")
            except mysql.connector.Error as c_err:
                print(f"Error creating table: {c_err}")
                db.rollback()
                raise SystemExit(1)
        else:
            print(f"Error checking table: {err}")
            raise SystemExit(1)
    finally:
        c.close()


def main():
    counter = 0
    skipped = 0
    # Obtain some facts
    if AUTO and (not APIKEY or not PATH):
        print("Error! Set for automation but PATH and APIKEY are not set!")
        raise SystemExit(1)

    if not PATH and not AUTO:
        PATH = input("Enter full path to movies to add: ")

    if not APIKEY and not AUTO:
        APIKEY = input("Enter your 873gear API key: ")

    db = connect_to_mysql()
    if not db:
        print("Unable to connect database!")
        raise SystemExit(1)

    if not check_table(db):
        print("Failure occured locating the movies table!")
        raise SystemExit(1)

    # Process items in the directory
    inventory = fetch_movie_ids(PATH, APIKEY)

    # Add the movies to MovieBot873
    print("Processing results and adding to MovieBot873 and your local database...")
    for item in tqdm(inventory):
        if add_movie(db, item, APIKEY):
            counter += 1
        else:
            skipped += 1

    db.close()

    # Terminate with feedback
    print(f"Done! {counter} items added. {skipped} items were skipped.")


if __name__ == "__main__":
    main()
