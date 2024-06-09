import os
from pytube import YouTube, Playlist
from pytube.cli import on_progress
import subprocess

def get_available_qualities(video_streams):
    qualities = []
    for stream in video_streams:
        if stream.resolution:
            qualities.append((stream.resolution, stream.filesize))

    # Remove duplicates        
    qualities = list(set(qualities))  

     # Sort by resolution
    return sorted(qualities, key=lambda x: int(x[0][:-1]), reverse=True) 

def choose_quality(qualities):
    print("\nAvailable qualities:")
    for idx, (quality, size) in enumerate(qualities, 1):
        print(f"{idx}. {quality} ({size / (1024*1024):.2f} MB)")
    choice = int(input("Enter the number of the desired quality: "))
    return qualities[choice - 1][0]

def download_video(url, quality=None):
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        video_streams = yt.streams.filter(file_extension='mp4').filter(adaptive=True)
        
        if not quality:
            available_qualities = get_available_qualities(video_streams)
            quality = choose_quality(available_qualities)

        video = video_streams.filter(res=quality, type='video').first()
        if not video:
            print(f"Video with resolution {quality} not available. Downloading highest resolution available.")
            video = video_streams.get_highest_resolution()

        audio = yt.streams.filter(only_audio=True, file_extension='mp4').first()

        # Downloading video
        print(f"Downloading video: {yt.title} in {quality}")
        video_file = video.download(filename=f"video_{yt.video_id}.mp4")
        print("Video downloaded")

        # Downloading Audio
        print("Downloading audio")
        audio_file = audio.download(filename=f"audio_{yt.video_id}.mp4")
        print("Audio downloaded")

        # Merge files 
        output_file = f"{yt.title}.mp4"
        print("Merging video and audio")
        merge_video_audio(video_file, audio_file, output_file)

        print(f"Downloaded and merged: {output_file}")

        os.remove(video_file)
        os.remove(audio_file)
    except Exception as e:
        print(f"Error downloading video: {e}")

def merge_video_audio(video_file, audio_file, output_file):
    command = [
        'ffmpeg',
        '-i', video_file,
        '-i', audio_file,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_file
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def download_playlist(url, quality=None):
    try:
        playlist = Playlist(url)
        print(f"Downloading playlist: {playlist.title}")

        if not quality:
            first_video_url = playlist.video_urls[0]
            yt = YouTube(first_video_url)
            video_streams = yt.streams.filter(file_extension='mp4').filter(adaptive=True)
            available_qualities = get_available_qualities(video_streams)
            quality = choose_quality(available_qualities)

        for video_url in playlist.video_urls:
            download_video(video_url, quality)
    except Exception as e:
        print(f"Error downloading playlist: {e}")

def main():
    print("YouTube Downloader")
    url = input("Enter the URL of the video or playlist: ")
    quality = None

    if 'playlist' in url:
        download_playlist(url, quality)
    else:
        download_video(url, quality)

if __name__ == "__main__":
    main()