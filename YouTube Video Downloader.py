from UILibrary import *
from pytube import YouTube
import subprocess
from pathlib import Path

ui = UI('YouTube Video Downloader')
c = ui.colors
s = ui.save_info
ui.style['ask_color'] = c.red
ui.style['progress_bar_color'] = c.red

resolutions = '4320p', '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p'

first = None


def download_progress(stream, chunk, bytes_remaining):
    global first
    global ui

    if first is None:
        first = bytes_remaining
    ui.progress_bar.update(first - bytes_remaining, first, 'Downloading video')


video = YouTube(ui.ask('Video URL'), on_progress_callback=download_progress)
stream = video.streams.order_by('bitrate').desc()
print(f'{c.reset}{c.bold}{video.title}{c.reset}{c.gray}    by    {c.reset}{c.bold}{video.author}{c.reset}{c.gray}    with    {c.reset}{c.bold}{video.views}{c.reset}{c.gray}    views.{c.reset}')
max_res = stream.first().resolution
ol = ui.OptionsList()
for i in resolutions[resolutions.index(max_res):]:
    if i == max_res:
        ol.add(i + ' (native)', i)
    else:
        ol.add(i)
ol.add('Audio only')
stream_choice = ol.show()

name = ui.ask('filename (no extension, leave blank to use the video title)')

bad_characters = '\\/:*?"<>|'
if name == '':
    name = video.title
for i in bad_characters:
    name = name.replace(i, '')
if name == '':
    name = 'Downloaded YouTube video'

audio = stream.get_audio_only()
working_folder = str(Path.cwd()).replace('\\', '/')
if stream_choice == 'Audio only':
    audio.download(filename=name)
else:
    video_stream = stream.filter(res=stream_choice).first()
    v_extension = video_stream.mime_type.split('/')[-1]
    a_extension = audio.mime_type.split('/')[-1]
    video_stream.download(filename='tmp_download_video')
    audio.download(filename='tmp_download_audio')

    subprocess.run(f'ffmpeg -i {working_folder}/tmp_download_video.{v_extension} -i {working_folder}/tmp_download_audio.{a_extension} -c copy "{working_folder}/{name}.mp4"')

print(c.green + '=' * 80)
print(c.reset + f'Video downloaded as {c.bold}{c.red}{name}{c.reset} at {c.bold}{working_folder}/{name}')
print('=' * 80)
