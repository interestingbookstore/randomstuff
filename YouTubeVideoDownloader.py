from UILibrary import *
from pytube import YouTube
from sys import argv
from os import system
from pathlib import Path

# -----------------------------------------
TMP_File_Save_Location = '/.tmp'
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


arguments = argv[1:]
# --------------------  Help commands  ----------------------------------------
if len(arguments) == 1 and (arguments[0] == '-h' or arguments[0] == '--help'):
    print(
        f"""
        This is a simplistic python script for downloading YouTube videos.
        It can be interacted with through it's built in UI, or entirely through terminal arguments.
        If the terminal arguments aren't present or raise an error, this script fallback to
        the UI for the unresolved parameters.
        
        In total, it uses three parameters; the {c.bold}{c.red}URL{c.reset} of the video,
        the {c.bold}{c.red}resolution{c.reset} of the video, and the {c.bold}{c.red}filename{c.reset} of the result.
        
        --------------------  Terminal  ----------------------------------------
        Via the terminal, you simply type in the parameters:
        {c.red}{'=' * 80}{c.reset}
        python    VideoDownloader.py    [URL]    [resolution]    [filename].
        {c.red}{'=' * 80}{c.reset}
        
        Note that you can type in "{c.bold}audio{c.reset}" (in place of the resolution) to
        download only the video's audio, as an audio file.
        
        Another note is that you can slightly automate the latter parameters; by typing in {c.bold}"max"{c.reset},
        this script will download the highest resolution version of the video. With that said, if you don't want
        a 5K, 8K version of the video, you can follow the keyword with the limit you want to set. For example, you
        can type in {c.bold}"max2160"{c.reset} to download the highest resolution of a video, but clip down anything
        above 2160p (e.g. 5K, 8K) back to 4k.
        
        Similarly, for the filename, you can type {c.bold}"/title"{c.reset} to use the video's title as the filename.
        Or, if you want to add a prefix and/or suffix, note that /title is just replaced with the video's title, but
        anything around it stays. So, you can type in {c.bold}"Downloaded video /title from <a YouTube channel>"{c.reset}
        if you wanted to, and everything would work!
        
        As a final note, adding that "p" (for pixels) at the end doesn't make a difference; you can type
        in {c.bold}"720"{c.reset} or {c.bold}"720p"{c.reset}. Either way, it'll be interpreted as 720p.
        
        --------------------  UI  ----------------------------------------
        There isn't as much to say about the UI, although there are a few tips.
        For one, not typing in anything when the option to choose a resolution comes
        up (i.e., immediately pressing enter) will default to the top result, the highest resolution.
        A second tip is that the "/title" feature mentioned above also works here. So, when you're asked
        to type in the filename, you can add /title at any point, and it'll be replaced with the video's title.
        
        """
    )

    ui.quit()
# --------------------  URL  ----------------------------------------
if len(arguments) >= 1:
    url = arguments[0]
else:
    url = ui.ask('Video URL')
# --------------------  Video stuff  ----------------------------------------
video = YouTube(url, on_progress_callback=download_progress)
stream = video.streams.order_by('bitrate').desc()
max_res = stream.first().resolution
print(f'{c.reset}{c.bold}{video.title}{c.reset}{c.gray}    by    '
      f'{c.reset}{c.bold}{video.author}{c.reset}{c.gray}    with    '
      f'{c.reset}{c.bold}{large_number_formatter(video.views)}{c.reset}{c.gray}    views at    '
      f'{c.reset}{c.bold}{video.length}{c.reset}{c.gray}    seconds long.{c.reset}')


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
    elif quality[:3] == 'max':
        if len(quality) > 3:
            maximum = quality[3:].strip('p')
            if int(maximum) > int(max_res.strip('p')):
                stream_choice = max_res
            else:
                maximum += 'p'
                if maximum in resolutions:
                    stream_choice = maximum
                else:
                    ui.error_print(f'"{quality}" is not a recognized quality. Available options are "4320p", "2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p", "max<limit>" or "audio"')
                    stream_choice = quality_ui()
        else:
            stream_choice = max_res
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
            ui.error_print(f'"{quality}" is not a recognized quality. Available options are "4320p", "2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p", "max<limit>" or "audio"')
            stream_choice = quality_ui()
else:
    stream_choice = quality_ui()

# --------------------  Name  ----------------------------------------
if len(arguments) >= 3:
    name = arguments[2]
else:
    name = ui.ask('filename (no extension, leave blank to use the video title)')

bad_characters = '\\/:*?"<>|'
name = name.replace('/title', video.title)
if name == '':
    name = video.title
for i in bad_characters:
    name = name.replace(i, '')
if name == '':
    name = 'Downloaded YouTube video'

# --------------------  Actual Stuff  ----------------------------------------
audio = stream.get_audio_only()
Save_Location = Save_Location.replace('\\', '/')
if stream_choice == 'Audio only':
    audio.download(output_path=Save_Location, filename=name)
else:
    video_stream = stream.filter(res=stream_choice).first()
    v_extension = video_stream.mime_type.split('/')[-1]
    a_extension = audio.mime_type.split('/')[-1]
    video_stream.download(output_path=TMP_File_Save_Location, filename='tmp_download_video')
    audio.download(output_path=TMP_File_Save_Location, filename='tmp_download_audio')

    system(f'ffmpeg -loglevel warning -i "{TMP_File_Save_Location}/tmp_download_video.{v_extension}" -i "{TMP_File_Save_Location}/tmp_download_audio.{a_extension}" -c copy "{Save_Location}/{name}.mp4"')

print(c.green + '=' * 80)
print(c.reset + f'Video downloaded as {c.bold}{c.red}{name}.mp4{c.reset} at {c.bold}{Save_Location}/{name}.mp4')
print('=' * 80)
