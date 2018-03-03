# Wallpaper Downloader

A command line application that allows a user to choose a 4Chan board (default: Wallpapers), search for keywords, then choose a thread to browse.

After choosing a thread, a GUI application opens which allows the user to browse through all of the images in that thread, and download the images of their choice.

Note - the pyglet-fixed folder is a hand-rolled modification of Pyglet that prevents crashes under specific circumstances.

## Usage

A board is chosen by the user | ![](https://i.imgur.com/p5ydiGQ.png)
:---: | ---
Keyword(s) are entered | ![](https://i.imgur.com/nCZnTY2.png)
A thread is chosen | ![](https://i.imgur.com/nqvTyaJ.png)
A GUI opens which allows the user to navigate and save images from the chosen thread. The controls are:<br>Up Arrow (or scroll wheel) - Zoom in<br>Down Arrow (or scroll wheel) - Zoom out<br>Left Arrow  - Navigate left one image<br>Right Arrow - Navigate right one image<br>Right-click near left or right edge - Navigate left or right<br>Left-click (drag) - Move image<br>Space - Save image<br>Enter - Play .webm file<br>r - Refresh thread (caches new images)<br>w - Open image in default web browser<br>s - Open thread in default web browser<br>6 (NUMPAD) - Rotate image 90 degrees clockwise<br>4 (NUMPAD) - Rotate image 90 degrees counterclockwise<br>0 - Change border style<br>v - View saved images | ![](https://i.imgur.com/GZ980RX.png)
If an image has yet to be cached, "No Preview Available" will be shown | ![](https://i.imgur.com/tHqu01J.png)
Pressing "v" will open another GUI which allows the user to view saved images (closing the viewer will bring the first GUI back into focus) | ![](https://i.imgur.com/D93pkmW.png)

## How it Works
1. The user is prompted for a board, enters keywords to search, and selects a thread from the provided search-list. The search-list is created using `find_thread` function, which crawls the chosen board and finds each instance of the keyphrase provided.
2. When a thread is chosen, the `list_images` function is ran, which fetches a list of all the images from the selected thread.
3. The `cache_images` function is ran asyncronously, which uses the list of images and downloads each, adding them to the `cache` folder.
4. After a brief 1 second delay (to allow the cacher to cache the first image), the `start` function is executed which opens an interactive Pyglet GUI, allowing the user to navigate, rotate, play, and save images/gifs from the selected thread.

## Built With

* Pyglet - Used for the GUI. Modified to prevent crashes under specific circumstances.
* Requests/urllib.request - Used to scrape the chosen board / download files.
* threading (python stl) - Used to download images asyncronously.
* html (python stl) - Used to unescape thread titles.
* webbrowser (python stl) - Used to open thread/image in the default web browser.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
