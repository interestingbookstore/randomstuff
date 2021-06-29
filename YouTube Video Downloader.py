from UILibrary import *
from pytube import YouTube
import subprocess
from pathlib import Path

ui = UI('YouTube Video Downloader')
c = ui.colors
s = ui.save_info
ui.style['ask_color'] = c.red

video = YouTube(ui.ask('Video URL'))
stream = video.streams.order_by('bitrate').desc()
print(f'{c.reset}{c.bold}{video.title}{c.reset}{c.gray}    by    {c.reset}{c.bold}{video.author}{c.reset}{c.gray}    with    {c.reset}{c.bold}{video.views}{c.reset}{c.gray}    views.{c.reset}')
stream.first().download(filename='tmp_download_video')
stream.get_audio_only().download(filename='tmp_download_audio')

name = ui.ask('filename (no extension, leave blank to use the video title)')
if name == '':
    name = video.title

working_folder = Path.cwd()
print(working_folder)
print(f'ffmpeg -i {working_folder}/tmp_download_video.mp4 -i {working_folder}/tmp_download_audio.mp4 -c copy {working_folder}/output.mp4')

subprocess.run(f'ffmpeg -i {working_folder}/tmp_download_video.mp4 -i {working_folder}/tmp_download_audio.mp4 -c copy {working_folder}/{name}.mp4')
