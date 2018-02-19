from importlib.machinery import SourceFileLoader

pyglet = SourceFileLoader("pygl", "pyglet-fixed\\__init__.py").load_module()
import urllib.request as ulib
import webbrowser as webb
import threading as thr
import requests as req
import base_viewer # base image viewer, used for viewing downloaded images.
import urllib
import shutil
import html
import time
import sys
import os

threads = [] ## As in 4chan threads, not thread objects...
downloaded = []
images = []

chosen_thread = {}

current = 0

nopreview = pyglet.image.load("resources\\nopreview.png")
sprite = pyglet.sprite.Sprite(nopreview)

global window
global sides
window_style = pyglet.window.Window.WINDOW_STYLE_DEFAULT
global location

cached = 0
cacher = None

screen_size = pyglet.window.Window(fullscreen = True)
screen_size.close()
screen_size = screen_size.get_size()

#player = pyglet.media.Player()
pyglet.media.SourceGroup.loop = True

first_played = False
## To scale the window back to normal...


def find_thread(search_query, board = "b"):
    global threads
    global chosen_thread
    global images
    page = 1
    thread = 1

    images = []
    print("Finding: " + search_query)
    while True:
        try:
            find_url = "http://a.4cdn.org/" + board + "/" + str(page) + ".json"
            res = req.get(find_url)
            res = res.json()
            for i in range(len(res["threads"])):
                try:
                    if res["threads"][i]["posts"][0]["com"].lower().find(search_query.lower()) != -1:
                        #print(str(res["threads"][i]["posts"][0]["no"]))
                        #print(res["threads"][i]["posts"][0]["semantic_url"])
                        good = html.unescape(res["threads"][i]["posts"][0]["com"]).replace("<br>", "\n").replace('<span class="quote">', "").replace("</span>", "")
                        print("["+str(thread)+"] " + good[:good.find("\n")])
                        threads.append({"thread_number" : res["threads"][i]["posts"][0]["no"],
                                        "semantic_url"  : res["threads"][i]["posts"][0]["semantic_url"],
                                        "board"         : board,
                                        "url"           : "http://boards.4chan.org/" + board + "/thread/" + str(res["threads"][i]["posts"][0]["no"]) + "/" + res["threads"][i]["posts"][0]["semantic_url"]})
                        thread += 1
                except KeyError:
                    None
            page += 1
        except ValueError:
            break
    if threads != []:
        chosen = input("Which thread would you like? (type # of thread, 0 to cancel)\n")
        if chosen == "all":
            chosen_thread = threads

        else:
            chosen = int(chosen) - 1
            if chosen != -1:
                chosen_thread = threads[chosen]
                    
    else:
        print("No threads found")


def list_images(thread_number = None, semantic_url = None, board = None, no_spam = False):
    global chosen_thread
    global label
    global images

    images = []

    if thread_number == None:
        thread_number = chosen_thread["thread_number"]

    if semantic_url == None:
        semantic_url = chosen_thread["semantic_url"]

    if board == None:
        board = chosen_thread["board"]
    
    url = "http://a.4cdn.org/" + board + "/thread/" + str(thread_number) + ".json"
    print(url)
    res = req.get(url).json()

    count = 1
    for i in res["posts"]:
        try:
            if no_spam == False:
                print("[" + str(count) + "] " + str(i["tim"]) + i["ext"])
            if (str(i["tim"]) + i["ext"]) not in images:
                images.append(str(i["tim"]) + i["ext"])
                count += 1
        except KeyError:
            None

    if no_spam == False:
        return images


def cache_images(recache = False):
    global images
    global chosen_thread
    global cached


    with open("resources\\data.txt") as f:
        f = f.read()
        try:
            if f.split("\n")[0] != chosen_thread["thread_number"] and \
               f.split("\n")[1] != chosen_thread["semantic_url"]:
                shutil.rmtree("cache", True)
                while True:
                    try:
                        os.mkdir("cache")
                        break
                    except:
                        print("Broke trying to create cache directory")
                        None
                    ### Keep trying until it works...
                with open("resources\\data.txt", "w") as f:
                    f.write(str(chosen_thread["thread_number"]) + "\n" + \
                    chosen_thread["semantic_url"] + "\n"+chosen_thread["board"])
        except IndexError:
            ## Nothing in data
            with open("resources\\data.txt", "w") as f:
                f.write(str(chosen_thread["thread_number"]) + "\n" + \
                    chosen_thread["semantic_url"] + "\n"+chosen_thread["board"])
            
    if recache == False:
        for folder, dirs, files in os.walk("cache", topdown=False):
            for name in files:
                cached += 1
    
    for image in images:
        if os.path.exists("cache/" + image) == False:
            while True:
                try:
                    ulib.urlretrieve("http://i.4cdn.org/" + chosen_thread["board"] + "/" + image, "cache/" + image)
                    break # this will stop the while loop
                except (urllib.error.ContentTooShortError, KeyError) as e:
                    if type(e) == KeyError:
                        ## The window was closed during caching
                        break
                    else:
                        ## The cacher receieved an imcomplete image!
                        print("Receieved an imcomplete image, trying again...")
                        None
            cached += 1
            try:
                window.set_caption(images[current] + " (image " + str(current + 1) + " out of " + str(len(images)) + ")" + " (" + str(cached) + " cached)")
            except:
                print("Caching")
                None


def queue_image(resize = False):
    global current
    global images
    global sprite
    global window
    global player
    try:
        if images[current][images[current].find("."):] == ".webm":
                sprite.image = pyglet.image.load("resources\\animated.png")
                window.set_size(sprite.width, sprite.height)
                
        elif images[current][images[current].find("."):] != ".gif":
            sprite.image = pyglet.image.load("cache/" + images[current])
            if sprite.rotation == 0 or sprite.rotation == 180:
                window.set_size(sprite.width, sprite.height)
            else:
                window.set_size(sprite.height, sprite.width)

        else:
            image = pyglet.resource.animation("cache/" + images[current])
            sprite.image = image
            window.set_size(sprite.width, sprite.height)
    except:
        sprite.image = pyglet.image.load("resources\\nopreview.png")
        window.set_size(sprite.width, sprite.height)

    if resize == False:
        return None # End the program early

    if window_style == pyglet.window.Window.WINDOW_STYLE_DEFAULT:
        try:
            sprite.scale = (screen_size[1] / sprite.image.height) - ((screen_size[1] / sprite.image.height) / 15)

            if sprite.width > screen_size[0]:
                sprite.scale = (screen_size[0] / sprite.image.width) - ((screen_size[0] / sprite.image.width) / 25)
        except:
            ## File is a GIF
            sprite.scale = (screen_size[1] / sprite.image.get_max_height()) - ((screen_size[1] / sprite.image.get_max_height()) / 15)

            if sprite.width > screen_size[0]:
                sprite.scale = (screen_size[0] / sprite.image.get_max_width()) - ((screen_size[0] / sprite.image.get_max_width()) / 25)
    else:
        try:
            sprite.scale = (screen_size[1] / sprite.image.height)

            if sprite.width > screen_size[0]:
                sprite.scale = (screen_size[0] / sprite.image.width)
        except:
            ## File is a GIF
            sprite.scale = (screen_size[1] / sprite.image.get_max_height())
            if sprite.width > screen_size[0]:
                sprite.scale = (screen_size[0] / sprite.image.get_max_width())

    window.set_size(sprite.width, sprite.height)
    sprite.rotation = 0
    sprite.x = 0
    sprite.y = 0


def start():
    global current
    global images
    global sprite
    global window, window_style
    global player
    global cacher
    window = pyglet.window.Window(style = window_style)
    window.set_location(7, 29)

    while True:
        try:
            if images[current][images[current].find("."):] == ".webm":
                sprite.image = pyglet.image.load("resources\\animated.png")
                window.set_size(sprite.width, sprite.height)
            
            elif images[current][images[current].find("."):] != ".gif":
                sprite.image = pyglet.image.load("cache\\" + images[current])
                window.set_size(sprite.width, sprite.height)

            else:
                ## is gif
                try:
                    player.delete()
                except:
                    print("ehh")
                image = pyglet.resource.animation("cache/" + images[current])
                while True:
                    try:
                        sprite.image = image
                        sprite.scale = 1.0
                        window.set_size(sprite.width, sprite.height)
                        break
                    except AttributeError:
                        ## Image is not yet cached
                        print("halp")
                        None
            break
        except FileNotFoundError:
            print("FILE NOT FOUND")
            break

    @window.event
    def on_close():
        cacher = None
        pyglet.app.exit() # Manually kill viewer (which is invisible) 
    
    @window.event
    def on_draw():
        global window
        global images
        global cached
        global current
        window.clear()
        if images[current][images[current].find("."):] == ".webm":
            sprite.draw()
        else:
            sprite.draw()

        filename = images[current][::-1]
        filename = filename[:filename.find("\\")]
        filename = filename[::-1]
        window.set_caption(filename + " (image " + str(current + 1) + " out of " + str(len(images)) + ")" + " (" + str(cached) + " cached)")


    @window.event
    def on_key_press(symbol, modifiers):
        global sprite
        global current
        global images
        global player
        global first_played
        global window, window_style, location
        global cacher
        key = pyglet.window.key
            
        if symbol == key.UP:
            ## Increase scale
            sprite.scale += 0.125

        elif symbol == key.DOWN:
            ## Decrease scale
            sprite.scale -= 0.125

        elif symbol == key.RIGHT:
            ## display next image
            current += 1
            if current > len(images) - 1:
                current = 0

        elif symbol == key.LEFT:
            ## Display previous image
            current -= 1
            if current < 0:
                current = len(images) - 1

        elif symbol == key.R:
            ## Refresh
            list_images(board = chosen_thread["board"])
            cacher = thr.Thread(target = cache_images, args=[True])
            cacher.start()

        elif symbol == key.SPACE:
            ## "Download" image
            if os.path.exists("Downloaded\\" + chosen_thread["semantic_url"]) == False:
                while True:
                    try:
                        os.mkdir("Downloaded\\" + chosen_thread["semantic_url"])
                        break
                    except PermissionError:
                        None
                ### Keep trying until it works...
            try:
                shutil.copy("cache\\" + images[current], "Downloaded\\" + chosen_thread["semantic_url"] + "\\" + images[current])

            except FileExistsError:
                ## File already "downloaded"
                None

            ding = pyglet.media.load("resources\\Ding_Sound_Effect.wav")
            ding.play()

        elif symbol == key.W:
            browser = webb.WindowsDefault()
            browser.open_new_tab("http://i.4cdn.org/" + chosen_thread["board"] + "/" + images[current])

        elif symbol == key.S:
            url = "http://a.4cdn.org/" + chosen_thread["board"] + "/thread/" + chosen_thread["thread_number"] + ".json"
            res = req.get(url).json()
            for i in res["posts"]:
                try:
                    if (str(i["tim"]) + i["ext"]) == images[current]:
                        browser = webb.WindowsDefault()
                        browser.open_new_tab("http://boards.4chan.org/" + chosen_thread["board"] + "/thread/" + chosen_thread["thread_number"] + "/" + chosen_thread["semantic_url"] + "#p"+ str(i["no"]))
                        break
                except KeyError:
                    ## Post does not have a file
                    None
        elif symbol == key.ENTER:
            if images[current][images[current].find("."):] == ".webm":
                source = pyglet.media.load("cache\\" + images[current])
                start_video(source)

        elif symbol == key.NUM_6:
            ## Rotate 90 degrees clockwise
            sprite.rotation += 90

            if sprite.rotation == 90 or sprite.rotation == -270:
                sprite.y += sprite.width
                window.set_size(sprite.height, sprite.width)

            elif sprite.rotation == 180 or sprite.rotation == -180:
                sprite.x += sprite.width
                sprite.y = 0
                sprite.y += sprite.height
                window.set_size(sprite.width, sprite.height)

            elif sprite.rotation == 270 or sprite.rotation == -90:
                sprite.x = 0
                sprite.y = 0
                sprite.x += sprite.height
                window.set_size(sprite.height, sprite.width)

            elif sprite.rotation == 360 or sprite.rotation == 0:
                sprite.x = 0
                sprite.y = 0
                sprite.rotation = 0
                window.set_size(sprite.width, sprite.height)

        elif symbol == key.NUM_4:
            ## Rotate 90 degrees clockwise
            sprite.rotation -= 90

            if sprite.rotation == 0 or sprite.rotation == -360:
                sprite.x = 0
                sprite.y = 0
                sprite.rotation = 0
                window.set_size(sprite.width, sprite.height)

            elif sprite.rotation == 90 or sprite.rotation == -270:
                sprite.x = 0
                sprite.y = 0
                sprite.y += sprite.width
                window.set_size(sprite.height, sprite.width)

            elif sprite.rotation == 180 or sprite.rotation == -180:
                sprite.x = 0
                sprite.y = 0
                sprite.x += sprite.width
                sprite.y += sprite.height
                window.set_size(sprite.width, sprite.height)

            elif sprite.rotation == 270 or sprite.rotation == -90:
                sprite.x = 0
                sprite.y = 0
                sprite.x += sprite.height
                window.set_size(sprite.height, sprite.width)

        elif symbol == key.V:
            window.set_visible(False)
            base_viewer.start("Downloaded\\" + chosen_thread["semantic_url"])

        elif symbol == key._0:
            location = window.get_location()
            if window_style == pyglet.window.Window.WINDOW_STYLE_DEFAULT:
                window_style = pyglet.window.Window.WINDOW_STYLE_BORDERLESS
            else:
                window_style = pyglet.window.Window.WINDOW_STYLE_DEFAULT
            window.close()
            start()
            window.set_location(location)
            

        if symbol == key.UP or symbol == key.DOWN or symbol == key.LEFT or symbol == key.RIGHT:
            if symbol == key.LEFT or symbol == key.RIGHT:
                queue_image(True)
            else:
                queue_image()

    @base_viewer.viewer.event
    def on_close():
        print("YOU ATTEMPTED TO CLOSE THE WINDOW")
        window.set_visible(True)

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        global sprite
        if buttons == 1:
            sprite.x += dx
            sprite.y += dy


    @window.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        global sprite
        if scroll_y == 1:
            ## Scrolled up
            sprite.scale += 0.125
            window.set_size(sprite.width, sprite.height)
        elif scroll_y == -1:
            ## Scrolled down
            sprite.scale -= 0.125
            window.set_size(sprite.width, sprite.height)

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        global current
        if button == 4:
            ## If right clicked...
            if x < (window.width / 3):
                ## Move back one...
                current -= 1
                if current < 0:
                    current = len(images) - 1

            elif (window.width - x) < (window.width / 3):
                ## Move forward one...
                current += 1
                if current > len(images) - 1:
                    current = 0
            queue_image(True)

        if button == 2:
            ## "Download" image
            if os.path.exists("Downloaded\\" + chosen_thread["semantic_url"]) == False:
                while True:
                    try:
                        os.mkdir("Downloaded\\" + chosen_thread["semantic_url"])
                        break
                    except PermissionError:
                        None
                ### Keep trying until it works...
            try:
                shutil.copy("cache\\" + images[current], "Downloaded\\" + chosen_thread["semantic_url"] + "\\" + images[current])

            except FileExistsError:
                ## File already "downloaded"
                None

            ding = pyglet.media.load("resources\\Ding_Sound_Effect.wav")
            ding.play()

    try:
        pyglet.app.run()
    except AttributeError:
        print("ctypes is a working, functional piece of software")


def start_video(video = None):
    try:
        global side
        global player
        side = pyglet.window.Window()
        player = pyglet.media.Player()

        @side.event
        def on_draw():
            global side
            global player
            side.clear()
            try:
                player.get_texture().blit(0, 0)
                time.sleep(0.05)
                sys.stdout.write(images[current] + " --> " + str(round(player.time, 2)) + " seconds / " + str(player.source.duration) + " seconds\r")
                sys.stdout.flush()
                side.set_caption(images[current] + " --> " + str(round(player.time, 2)) + " seconds / " + str(player.source.duration) + " seconds")
                if player.source.duration - player.time < 1:
                    #pyglet.app.exit()
                    player.delete()
                    side.close()
                    del side
                    del player
            except:
                print("FUCK")
                None

        @side.event
        def on_key_press(symbol, modifiers):
            global player, side
            key = pyglet.window.key

            if symbol == key.UP:
                print("UP")

            
        if video != None:
            player.queue(video)
            #player.pitch = 2.0
            side.set_size(player.source.video_format.width, player.source.video_format.height)
            try:
                player.play()
            except:
                print("oh")

        pyglet.app.run()

    except AttributeError:
        ## Video finished...........
        print("\nFINISHED")
        None



def auto(search_query, board = "b", last = False):
    global threads
    global chosen_thread
    find_thread(search_query, board)
    if threads != [] and chosen_thread != {}:
        list_images(board = board)
        cacher = thr.Thread(target = cache_images)
        cacher.start()
        time.sleep(1)
        start()


while True:
    try:
        board = input("Enter Board (automatically chooses /b/):\n")
        if board == "--last":
            with open("resources\\data.txt") as f:
                f = f.read()
                chosen_thread.update({"thread_number" : f.split("\n")[0],
                                      "semantic_url"  : f.split("\n")[1],
                                      "board"         : f.split("\n")[2]})
                try:
                    list_images()
                except:
                    ## Thread deleted
                    images = [os.path.join("",fn) for fn in next(os.walk("cache"))[2]]
                cacher = thr.Thread(target = cache_images)
                try:
                    cacher.start()
                except:
                    ## Thread deleted...
                    None
                time.sleep(1)
                start()
        elif board == "--exit":
            break
        
        else:
            search = input("Enter search query:\n")

            if board == "":
                board = "b"

            auto(search, board)

            threads = []
            chosen_thread = {}
            current = 0
            cached = 0
    except:
        break

