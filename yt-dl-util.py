#!/usr/bin/env python3

from pytube import YouTube
import os

def main():
    path = input("Full path to save location: ")
    if path == "":
        path = os.getcwd()
    url = input("Give me a link: ")
    yt = YouTube(url)
    
    action = input("Manual, Audio, or automatic? ")
    if action.lower() in ['m', 'manual', 'man']:
        res = input("Filter resolution: ")
        ext = input("Filter extension: ")
        data = yt.streams.filter(progressive=True, resolution=res, file_extension=ext)
        for item in data:
            print(item)
        
        get_tag = input("Which itag to fetch? ")
        stream = data.get_by_itag(get_tag)
        stream.download(path)
    elif action.lower() in ["audio", "a"]:
        data = yt.streams.filter(only_audio=True)
        for item in data:
            print(item)

        get_tag = input("Which itag to fetch? ")
        stream = data.get_by_itag(get_tag)
        stream.download(path)
    else:
        data = yt.streams.filter(progressive=True, resolution='720p', file_extension='mp4')

        stream = data.first()
        print(f"Downloading: {stream.title} {stream.resolution} {stream.itag}")
        stream.download(path)

if __name__ == "__main__":
    main()
