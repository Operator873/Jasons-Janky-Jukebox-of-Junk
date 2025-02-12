#!/usr/bin/env python3

from tqdm import tqdm
import mysql.connector

SERVER = "yourserver"
DBUSER = "yourusername"
DBPASS = "yourpassword"
DBNAME = "yourmoviebotdatabasename"


def do_sql(query, args, action):
    db = mysql.connector.connect(
        host=SERVER, user=DBUSER, password=DBPASS, database=DBNAME
    )

    c = db.cursor()

    try:
        if args:
            c.execute(query, args)
        else:
            c.execute(query)

        if action.lower() == "commit":
            db.commit()
            return True

        if action.lower() == "all":
            return c.fetchall()

        return c.fetchone()
    except Exception as e:
        print(str(e))
    finally:
        db.disconnect()


def get_movies():
    return do_sql("""SELECT * FROM movies;""", None, "all")


def collapse(owners):
    cleaned = []
    [cleaned.append(x) for x in owners if x not in cleaned]
    return cleaned


def main():
    movies = get_movies()
    update_statement = """UPDATE movies SET owner=%s WHERE tmdbid=%s;"""
    modified = 0

    for movie in tqdm(movies):
        _title, _year, tmdbid, owner = movie
        new_list = collapse(owner.split(","))

        do_sql(update_statement, (",".join(new_list), tmdbid), "commit")
        modified += 1

    print(f"Done! {modified} records updated.")


if __name__ == "__main__":
    main()
