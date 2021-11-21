import sys

try:
	from UILibrary import *
except ModuleNotFoundError:
	print('\33[31mThis Python script requires my UILibrary to function, which you can get at \33[1mhttps://github.com/interestingbookstore/randomstuff')
	sys.exit()
try:
	from pytube import YouTube
except ModuleNotFoundError:
	print('\33[31mThis Python script requires the module pytube to function, which you can install with "pip install pytube"')
	sys.exit()
from pathlib import Path
from string import ascii_letters, digits
import re

# Version 2.0.0 Alpha November 21 2021
# -----------------------------------------
TMP_File_Save_Location = '/tmp'  # By default, the two temporary audio and video files are saved in "/tmp".
Save_Location = f'{str(Path.home())}/Downloads'  # By default, the any videos you download will be saved in the downloads folder.
#     (This should be a folder)                    Simply edit this line if you'd like to save them somewhere else.

default_quality = None  # Say you always want the top resolution, but nothing above 8K, for example (8K is a bit overkill, eh?). Simply set
#                         this variable to '4K', and you'll never have to specify again! If you want this feature disabled, keep this variable
#                         at None.

default_filename = '{title}'  # Similarly to the previous option, you can automatically set the filename to a default filename. How would
#                               that work? Well, you can use things like {title}, which adjust dynamically based on the video! See more below.

ask_save_location = False  # Say you're weird and want to be prompted for the save location the whenever downloading one or multiple
#                            video; just set this to True. Otherwise, False.

formatting = True  # By default, this script uses ANSI escape sequences to add color and text effects to certain elements.
#                    Normally, these wouldn't actually be visible, and they'd simply modify how the text looks. However, applications
#                    (like Windows's Command Prompt) still render them (and they don't actually change anything there), which looks a bit
#                    odd. So, if you're in a similar situation, or you simply dislike ANSI escape sequences, set this variable to "False"
#                    to disable them.

def _filename_process(filename):
	# Say you want to automate everything, including the filenames. After you've set the default filename (although this will work
	# regardless), add whatever processing you want for the filename here.

	# Example:
	# filename = filename.replace(' ', '_')

	return filename


# When choosing a filename, you can specify a couple "dynamic" strings.
# These include:

# {title} _or_ {name} -> The video's title
# {author} -> The channel that posted the video
# And, because why not;
# {views} -> The raw number of views the video has
# {length} -> The video's length (in seconds)

# If these are in the filename, they're replaced with the video's value for them.
# -----------------------------------------

ui = UI(formatting=formatting)
c = ui.colors
ui.style['ask_color'] = c.red
ui.style['options_list_number'] = c.red
ui.style['progress_bar_color'] = c.red

stream_size = 0
currently_downloading = 'video'

if not ui.check_if_terminal_command_exists('ffmpeg'):  # This isn't fully working for now, it'll be fixed in a future update.
	print(f"{ui.colors.red}This python script requires {ui.colors.bold}ffmpeg{ui.colors.reset}{ui.colors.red} to stitch the final video together, which you\ndon't seem to have installed. You can find it on FFmpeg's official website; {ui.colors.bold}ffmpeg.org")
	ui.quit()


def download_progress(stream, chunk, bytes_remaining):
	ui.progress_bar.update(stream_size - bytes_remaining, stream_size, f'Downloading {currently_downloading}')


resolutions = {'240': '240', '240p': '240', 'qvga': '240',
			   '360': '360', '360p': '360',
			   '480': '480', '480p': '480', 'vga': '480', 'ntsc': '480', 'wvga': '480',
			   '720': '720', '720p': '720', 'hd': '720', 'hd720': '720', 'hd 720': '720', '720hd': '720', '720 hd': '720',
			   '1080': '1080', '1080p': '1080', 'fullhd': '1080', 'full hd': '1080', 'full-hd': '1080', 'fhd': '1080', 'hd 1080': '1080', 'hd1080': '1080', '1080 hd': '1080', '1080hd': '1080',
			   '1440': '1440', '1440p': '1440', 'wqhd': '1440', '3k': '1440',
			   '2160': '2160', '2160p': '2160', '4k': '2160', 'uhd': '2160', 'uhd4k': '2160', 'uhd 4k': '2160', '4kuhd': '2160', '4k uhd': '2160',
			   '4320': '4320', '4320p': '4320', '8k': '4320', 'uhd8k': '4320', 'uhd 8k': '4320', '8kuhd': '4320', '8k uhd': '4320', 'max': '4320'}

video_id_characters = ascii_letters + digits + '-_'

args = ui.get_console_arguments()

if default_quality is not None:
	if default_quality.lower() not in resolutions:
		raise Exception(f'Default quality should be either "None" or a valid resolution, but "{default_quality}" given.')
if Save_Location[-1] == '/':
	Save_Location = Save_Location[:-1]
urls = []
qualities = []
filenames = []

for i in args:
	if (match := re.search('[a-zA-Z0-9_-]{11}', i)):
		urls.append('v=' + i[match.start():match.end()])
	elif i.lower() in resolutions:
		qualities.append(resolutions[i.lower()])
	else:
		filenames.append(i)

if len(urls) == 0:
	while True:
		urls = []
		urls2 = ui.ask('Video URL(s)', tuple)
		continue_going = False
		for i in urls2:
			if ' ' not in i and (match := re.search('[a-zA-Z0-9_-]{11}', i)):
				urls.append('v=' + i[match.start():match.end()])
			else:
				ui.error_print(f'The URL {i} is not a valid URL.')
				continue_going = True
		if not continue_going:
			break

prompt_suffix_prefix = '' if len(urls) == 1 else '(s)'
# The prefix of the prompt's suffix.

if len(qualities) == 0:
	if default_quality is not None:
		qualities.append(resolutions[default_quality.lower()])
	else:
		qualities2 = ui.ask(f'Video quality{prompt_suffix_prefix}', tuple)
		for i in qualities2:
			if i.lower() in resolutions:
				qualities.append(resolutions[i.lower()])

if len(filenames) == 0:
	if default_filename is not None:
		filenames.append(default_filename)
	else:
		filenames = ui.ask(f'Video filename{prompt_suffix_prefix}', tuple)

if ask_save_location:
	Save_Location = ui.ask(f'Save Location{prompt_suffix_prefix}')

final_videos = [[i] for i in urls]
for index, video in enumerate(final_videos):
	final_videos[index][0] = YouTube(video[0], download_progress)

if len(qualities) == 1:
	for index, _ in enumerate(final_videos):
		final_videos[index].append(qualities[0])
elif len(qualities) == len(urls):
	for index, i in enumerate(qualities):
		final_videos[index].append(i)
else:
	raise Exception(f'One or {len(urls)} qualities were expected, but {len(qualities)} were given;\n{qualities}')

if len(filenames) == 1:
	for index, _ in enumerate(final_videos):
		video = final_videos[index][0]
		final_videos[index].append(filenames[0].replace('{title}', video.title).replace('{name}', video.title).replace('{author}', video.author).replace('{views}', str(video.views)).replace('{length}', str(video.length)))
elif len(filenames) == len(urls):
	for index, i in enumerate(filenames):
		final_videos[index].append(i)
else:
	raise Exception(f'{len(urls)} filenames were expected, but {len(filenames)} were given;\n{filenames}')

for video in final_videos:
	print(f'{c.reset}{c.bold}{video[0].title}{c.reset}{c.gray}    by    '
		  f'{c.reset}{c.bold}{video[0].author}{c.reset}{c.gray}    with    '
		  f'{c.reset}{c.bold}{large_number_formatter(video[0].views)}{c.reset}{c.gray}    views at    '
		  f'{c.reset}{c.bold}{time_formatter(video[0].length)}{c.reset}{c.gray}    long.{c.reset}')

for video in final_videos:
	yt_object = video[0]
	quality = video[1]
	filename = video[2]

	filename = _filename_process(filename)

	streams_object = yt_object.streams.order_by('bitrate').desc()

	audio = streams_object.get_audio_only()
	if quality == 'audio':
		audio.download(output_path=Save_Location, filename=filename)
	else:
		video_streams = streams_object.filter(only_video=True, adaptive=True)
		max_res = video_streams.first().resolution[:-1]
		if int(quality) > int(max_res):
			quality = max_res
		video_stream = video_streams.filter(res=quality + 'p').first()
		v_extension = video_stream.mime_type.split('/')[-1]
		a_extension = audio.mime_type.split('/')[-1]
		stream_size = video_stream.filesize
		currently_downloading = 'video'
		video_stream.download(output_path=TMP_File_Save_Location, filename=f'tmp_download_video.{v_extension}')
		currently_downloading = 'audio'
		audio.download(output_path=TMP_File_Save_Location, filename=f'tmp_download_audio.{a_extension}')

		filename = ui.remove_invalid_filename_characters(filename).replace('/', '').replace('\\', '')
		name = ui.get_unique_file(f'{Save_Location}/{filename}.mp4')
		short_name = filename + '.mp4'

		ui.run_terminal_command(f'ffmpeg -loglevel warning -i "{TMP_File_Save_Location}/tmp_download_video.{v_extension}" -i "{TMP_File_Save_Location}/tmp_download_audio.{a_extension}" -c copy "{name}"')
		if ui.check_if_file_exists(name):
			print(f"Video saved as {short_name} at {name}")
		else:
			print(f"The video file wasn't successfully saved, :(")
