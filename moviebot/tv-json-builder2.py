import os
import re
import json
import requests


def main():
    print("HEADS UP! This script expects filebot style names like:")
    print("'Night Court - 1x01 - All You Need is Love.avi')")
    print("OR")
    print("Brooklyn Nine-Nine - S1E15 - Operation: Broken Feather.mkv")
    print("The '1x01'/'S1E01' format is matched for understanding season/episode/title\n")
    print("The folder containing all TV shows should NOT have shows nested in other show's directories.")

    path_to_tv = input("Full path to folder containing ALL TV: ")

    # Or can be full path to outfile you desire
    owner = input("Owner name as will appear in Owner list: ")

    data = process_shows(path_to_tv)

    with open(owner, 'w') as f:
        json.dump(data, f, indent=2)


def tmdb_api_search(title, year=None):
    apikey = "yourapikey"
    apiurl = "https://api.themoviedb.org/3/search/tv"

    query = {"query": title, "language": "en-US", "apikey": apikey}

    if year:
        query['first_air_date_year'] = year
    
    data = requests.get(apiurl, params=query).json()

    if "total_results" in data and data['total_results'] == 1:
        return data['results'][0]
    else:
        return False


def tmdb_api_fetch(item_id):
    apikey = "yourapikey"
    apiurl = f"https://api.themoviedb.org/3/tv/{item_id}"

    data = requests.get(apiurl, params={"apikey": apikey}).json()

    if "success" in data:
        return False
    else:
        return data


def process_shows(path):
    results = {}
    year_pattern = r"\([0-9]{4}\)"
    error_container = []
    shows = [(f.name, f.path) for f in os.scandir(path) if f.is_dir()]

    for show, path in shows:
        if not re.search(year_pattern, show):
            error_container.append(show)
            print(f"Skipping {show} - Couldn't find first aired year in name.")
        
        title, year = show.split(' (', 1)
        show_id = tmdb_api_search(title, year.replace(')', ''))['id']

        show_info = tmdb_api_fetch(show_id)

        results[show_id] = {
            "title": title,
            "year": year.replace(')', ''),
            "total_seasons": show_info['season_number'],
            "total_episodes": show_info['number_of_episodes']
        }

        seasons = 0
        episodes = 0

        
