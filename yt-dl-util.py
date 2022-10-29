from pytube import YouTube

def main():
    path = input("Full path to save location: ")
    url = input("Give me a link: ")
    yt = YouTube(url)
    
    action = input("Manual or automatic? ")
    if action.lower() in ['m', 'manual', 'man']:
        res = input("Filter resolution: ")
        ext = input("Filter extension: ")
        data = yt.streams.filter(progressive=True, resolution=res, file_extension=ext)
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
