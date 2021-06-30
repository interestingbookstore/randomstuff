from UILibrary import *
from pytube import YouTube
import os
import sys
from pathlib import Path

# -----------------------------------------
Save_Location = str(Path.cwd())  # By default the tmp files and output files are saved in the current working directory.
#     (No slash at the end!!)      Simply edit this line if you'd like to save them somewhere else.
# -----------------------------------------

ui = UI()
c = ui.colors
ui.style['ask_color'] = c.red
ui.style['options_list_number'] = c.red
ui.style['progress_bar_color'] = c.red

resolutions = '4320p', '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p'

first = None


def download_progress(stream, chunk, bytes_remaining):
    global first
    global ui

    if first is None:
        first = bytes_remaining
    ui.progress_bar.update(first - bytes_remaining, first, 'Downloading video')


# arguments = sys.argv[1:]
arguments = ['https://www.youtube.com/watch?v=oAHbLRjF0vo', '1080', 'idk']
# --------------------  URL  ----------------------------------------
if len(arguments) >= 1:
    url = arguments[0]
else:
    url = ui.ask('Video URL')
# --------------------  Video stuff  ----------------------------------------
video = YouTube(url, on_progress_callback=download_progress)
stream = video.streams.order_by('bitrate').desc()
max_res = stream.first().resolution
print(f'{c.reset}{c.bold}{video.title}{c.reset}{c.gray}    by    {c.reset}{c.bold}{video.author}{c.reset}{c.gray}    with    {c.reset}{c.bold}{large_number_formatter(video.views)}{c.reset}{c.gray}    views at    {c.reset}{c.bold}{video.length}{c.reset}{c.gray}    seconds long.{c.reset}')


# --------------------  Quality  ----------------------------------------
def quality_ui():
    ol = ui.OptionsList()
    for i in resolutions[resolutions.index(max_res):]:
        if i == max_res:
            ol.add(i + ' (native)', i)
        else:
            ol.add(i)
    ol.add('Audio only')
    return ol.show()


if len(arguments) >= 2:
    quality = arguments[1].lower()
    if quality == 'audio':
        stream_choice = 'Audio only'
    else:
        if quality.isdigit() and quality in [i[:-1] for i in resolutions]:
            quality += 'p'
        if quality in resolutions:
            if int(quality[:-1]) > int(max_res[:-1]):
                ui.error_print(f'{quality} is higher than the maximum resolution of the video, that being {max_res}.')
                stream_choice = quality_ui()
            else:
                stream_choice = quality
        else:
            ui.error_print(f'"{quality}" is not a recognized quality. Available options are "4320p", "2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p", or "audio"')
            stream_choice = quality_ui()
else:
    stream_choice = quality_ui()

# --------------------  Name  ----------------------------------------
if len(arguments) >= 3:
    name = arguments[2]
else:
    name = ui.ask('filename (no extension, leave blank to use the video title)')

bad_characters = '\\/:*?"<>|'
if name == '':
    name = video.title
for i in bad_characters:
    name = name.replace(i, '')
if name == '':
    name = 'Downloaded YouTube video'

audio = stream.get_audio_only()
Save_Location = Save_Location.replace('\\', '/')
if stream_choice == 'Audio only':
    audio.download(output_path=Save_Location, filename=name)
else:
    video_stream = stream.filter(res=stream_choice).first()
    v_extension = video_stream.mime_type.split('/')[-1]
    a_extension = audio.mime_type.split('/')[-1]
    video_stream.download(output_path=Save_Location, filename='tmp_download_video')
    audio.download(output_path=Save_Location, filename='tmp_download_audio')

    os.system(f'ffmpeg -loglevel warning -i "{Save_Location}/tmp_download_video.{v_extension}" -i "{Save_Location}/tmp_download_audio.{a_extension}" -c copy "{Save_Location}/{name}.mp4"')

print(c.green + '=' * 80)
print(c.reset + f'Video downloaded as {c.bold}{c.red}{name}.mp4{c.reset} at {c.bold}{Save_Location}/{name}.mp4')
print('=' * 80)
