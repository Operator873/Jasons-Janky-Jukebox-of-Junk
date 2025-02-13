#!/usr/bin/env python3

import sys
import json

import mysql.connector
import requests
from tqdm import tqdm

# MySQL/MariaDB config
HOST = "xxx.xxx.xxx.xxx"  # The IP of your database. "localhost" is also acceptable
USER = "myCoolUser"  # The username to connect to the database with
PASSWD = "123abc"  # The password for the above user
DBASE = "Plex"  # The name of the database in MySQL/MariaDB to use
TABLE = "Movies"  # The name of the table within the database to use

# 873gear API key
APIKEY = None  # Replace with your 873gear API key (str)

def connect_to_mysql():
    try:
        mydb = mysql.connector.connect(
            host=HOST, user=USER, password=PASSWD, database=DBASE, charset="utf8mb4"
        )
        print("Database Connection successful!")
        return mydb
    except mysql.connector.Error as e:
        if e.errno == 2003:
            print("Connection timed out or server not found.")
        else:
            print(f"Connection error: {e}")
        return None


def check_table(db):
    c = db.cursor()
    try:
        c.execute(f"SELECT * FROM {TABLE} LIMIT 1")
        c.fetchone()
    except mysql.connector.Error as err:
        if err.errno == 1146:
            check = input(f"Table '{TABLE}' not found in {DBASE}! Should I create it? ([Y]/n) ")
            if check.lower() not in ['y', 'yes', '']:
                print("Aborting run...")
                sys.exit(1)
            
            # Create table with defined schema that matches website
            create_table = f"""
            CREATE TABLE {TABLE} (
                tmdbID INT PRIMARY KEY,
                movieTitle VARCHAR(255) NOT NULL,
                movieImage VARCHAR(255),
                movieYear YEAR(4),
                movieGenre VARCHAR(255),
                movieDescription TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            try:
                c.execute(create_table)
                db.commit()
                print("Movies table created!")
            except mysql.connector.Error as c_err:
                print(f"Error creating table: {c_err}")
                db.rollback()
                sys.exit(1)
        else:
            print(f"Error checking table: {err}")
            sys.exit(1)
    finally:
        c.close()


def check_for_duplicates(title, year, data):
    # Make sure we got useful info
    try:
        if data["success"] and len(data["results"]) > 1:
            dupes = []
            # Check for duplicates and discard invalid or items missing info
            for item in data["results"]:
                if item["title"].lower() == title.lower() and item["year"] == year and not item["image"].endswith("None"):
                    dupes.append(item)

            # We found some dupes... Lets get input
            if len(dupes) > 1:
                count = 1
                print("Multiple matches found!", file=sys.stdout)
                for dupe in dupes:
                    print(f"Option {count}: {dupe['invid']} - {dupe['title']} ({dupe['year']}) - {dupe['image']}")
                    count += 1
                choice = int(input("Which option # is correct? (int) ")) - 1
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
        sys.exit(1)
    
    return result
    

def add_movie(db, movie, apikey):
    # Build a payload for 873gear to interrogate
    payload = {
        "query": "bot",
        "type": "movie",
        "title": movie["title"],
        "year": movie["year"],
        "apikey": apikey,
    }

    # Process out response for duplicates
    data = check_for_duplicates(movie["title"], movie["year"], xmit(payload))

    # Sanity check
    if not data:
        print(f"Error occurred processing {movie}. Skipping...")
        return False

    # Fetch detailed information for movie
    query = {
        "query": "bot",
        "type": "movie",
        "invid": data["invid"],
        "apikey": apikey,
    }

    info = xmit(query)["results"][0]

    # Begin local database operations
    c = db.cursor()
    check = f"SELECT tmdbID FROM {TABLE} WHERE tmdbID = %s"
    insert = f"INSERT INTO {TABLE} (tmdbID, movieTitle, movieImage, movieYear, movieGenre, movieDescription) VALUES (%s, %s, %s, %s, %s, %s)"
    
    # Check to see if item is already in the database
    c.execute(check, (info["invid"],))
    exists = c.fetchone()

    # It's not, so lets add it.
    if not exists:
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
            print(f"MySQL Error inserting: {values}! Rolling back... Error was: {e}")
        finally:
            c.close()
    
    # Add to 873gear database
    query = {
        "invid": info["invid"],
        "add": "movie",
        "apikey": apikey,
    }

    # Verify 873gear handled the transaction correctly.
    validate = xmit(query, "post")
    try:
        if validate["requestor"] not in validate["response"]:
            print(f"Unexpected response from 873gear! Payload was: {json.dumps(validate, indent=2)}")
    except TypeError:
        print(f"Error updating 873gear database! {json.dumps(validate, indent=2)}")
        return False
    
    return True


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


def main():
    counter = 0
    skipped = 0
    global APIKEY
    # Obtain some facts
    path = input("Fully qualified path to JSON file: ")

    if not APIKEY:
        APIKEY = input("Enter your 873gear API key: ")

    db = connect_to_mysql()

    if not db:
        print("Unable to connect database!")
        sys.exit(1)

    check_table(db)
    
    # Process items in the file
    print("Reading file...")
    with open(path, 'r') as f:
        inventory = json.loads(f.read())

    # Add the movies to MovieBot873 and local database
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
