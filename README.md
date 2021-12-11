# YouTube Video Downloader
I occasionally wanted to download a YouTube video, but instead of using an application that someone else made, I decided to make my own! It utilizes [pytube](https://pypi.org/project/pytube), [FFmpeg](https://ffmpeg.org), and my very own UILibrary to find a video from a URL, download two temporary versions for the video and audio respectively (the highest quality versions that you watch are actually split into seperate video and audio files, who knew), then merge them together with FFmpeg. My python script allows you to select from YouTube's available resolution options (which all get the highest quality video for that resolution as well as the highest quality audio) or simply download the audio, at the highest quality of course. By popular request, this script is also intractable through terminal arguments ("URL", "Quality", "Filename"). And, you get a progress bar! (I've noticed that somehow, pytube finishes downloading videos a decent while before it claims to in its progress updates... which is odd... (update, this issue has been fixed as of version 1.1. You may now be asking why I kept this, well, it's better for this description's pacing, I think...)). Anyway, there you go, you can download videos! (another update, version 2.0 is in the works, which will feature a couple of improvements. But if you want a real update, just you wait for the PyBookVideoDownloader...)

# UILibrary
Ever asked the user for an integer, only to have your program crash because the user gave something that is not an integer? Well, this library is here to fix that! (As well as a bunch of other stuff). You can use the `ask` method for the problem mentioned above, use the `large_number_formatter` to turn "1000" into "1K", turn "314159265" seconds into "*1 year, 5 months, 9 weeks, 3 days, 2 hours, 27 minutes and 45 seconds*", run terminal commands, get terminal arguments; option lists, unique files, progress bars, clipboard without modules, there's a lot. And, I've added it all into this one library that has zero documentation. Enjoy!

# PythonPoint
This is still a work in progress (me from the future, there's isn't much progress anymore), but it's supposed to do something kind of similar to what Microsoft PowerPoint and Google Slides do, but with a txt file, and it exports images. It's no where near as feature-rich compared to the aforementioned software, but I think that it's cool; it supports text, images, and variables. As a note, I included some fonts with the Python file, all of the fonts are from Google Fonts, and should be fine to use. Most use the SIL Open Fonts License, although Roboto is distributed under the Apache License Version 2, so keep all of these in mind. If you want any more fonts, you should be able to add them into the Fonts folder, and the If statements shoudld take care of the rest. Note, the If statements were designed with Google Fonts's format in mind, so, you could try to follow the naming scheme of all the other fonts if necessary.

# Image Cropping Tool
I started this as a fun quick project to make with my PyBook Engine... turned out, it wasn't quick. It was actually the most difficult programming project I've worked on. Anyway, in terms of what it does, it crops images. In terms of how to use it, you drag in an image, or paste one in with Ctrl-V (Windows and MacOS only). Then, you click and drag to make a selection. Then, you drag the corners/side/center to resize or move the selection. Then, you press Enter (technically Return) to save it, to the path listed in the options at the top of the file. Note, if the file already exists, it'll add a number at the end, and try again. So, no overwriting. More notes, you can use Shift and Ctrl to crop more precisely, and alt to mirror any adjustments. So, there, you can crop images!

# PyBookEngine
This is something I worked on mostly some time ago, although occasionally I might update it a bit. The way it's supposed to work is you interact with it, and it interacts with PyGame. Why might you want it? Well, it simplifies many aspects of making something with PyGame, by doing a lot of the work for you. For instance, it handles updating the screen all by itself. No more do you need to deal with the reduced performance of `pygame.display.flip`, nor the complexity of `pygame.display.update(`With all of those rects`)`. It'll do all of that for you. Similarly, if you close the application, it closes! (Which is in fact something you need to add in) And, it supports many handy features, including automatic conversion between Pillow images, image paths, to the normal pygame surfaces. It even has a built in drop shadow feature! Now, with all of that said, I don't work on it too much anymore, meaning that some features may be a bit underdeveloped, with other things not having been implemented at all. Although, it does have the origin on the bottom left, so, that's cool...
