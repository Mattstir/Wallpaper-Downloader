import pyglet
import os

viewer = pyglet.window.Window(resizable = True)

viewer.close = lambda:viewer.set_visible(False)
## Sets the window invisible instead of closing the window...
viewer.set_visible(False)
current = 0

screen_size = pyglet.window.Window(fullscreen = True)
screen_size.close()
screen_size = screen_size.get_size()

def queue_image():
    global current
    global images
    global sprite
    global viewer
    try:
        if images[current][images[current].find("."):] == ".webm":
            sprite.image = pyglet.image.load("resources\\nopreview.png")
            viewer.set_size(sprite.width, sprite.height)
        
        elif images[current][images[current].find("."):] != ".gif":
            sprite.image = pyglet.image.load(images[current])
            viewer.set_size(sprite.width, sprite.height)

        else:
            ## is gif
            try:
                player.delete()
            except:
                None
            image = pyglet.resource.animation(images[current])
            sprite.image = image
            viewer.set_size(sprite.width, sprite.height)
    except:
        sprite.image = pyglet.image.load("resources\\nopreview.png")
        viewer.set_size(sprite.width, sprite.height)


def start(filepath):
    global current
    global images
    global sprite
    global viewer
    global player
    images = [os.path.join(filepath,fn) for fn in next(os.walk(filepath))[2]]

    current = 0

    sprite = pyglet.sprite.Sprite(pyglet.image.load(images[0]))

    if images == []:
        ## If somehow no images were found
        print("Images were indexed, however none were available for caching")
        time.sleep(3)
        return None
        ## Ends the function

    viewer.set_visible(True)
    sprite.scale = (screen_size[1] / sprite.image.height) - ((screen_size[1] / sprite.image.height) / 15)
    viewer.set_size(sprite.width, sprite.height)

    while True:
        try:
            if images[current][images[current].find("."):] == ".webm":
                sprite.image = pyglet.image.load("resources\\nopreview.png")
                viewer.set_size(sprite.width, sprite.height)
            
            elif images[current][images[current].find("."):] != ".gif":
                sprite.image = pyglet.image.load(images[current])
                viewer.set_size(sprite.width, sprite.height)

            else:
                ## is gif
                try:
                    player.delete()
                except:
                    None
                image = pyglet.resource.animation(images[current])
                while True:
                    try:
                        sprite.image = image
                        sprite.scale = 1.0
                        viewer.set_size(sprite.width, sprite.height)
                        break
                    except AttributeError:
                        ## Image is not yet cached
                        print("halp")
                        None
            break
        except FileNotFoundError:
            print("FILE NOT FOUND")
            None
                
    
    @viewer.event
    def on_draw():
        global viewer
        global images
        global cached
        global current
        viewer.clear()
        if images[current][images[current].find("."):] == ".webm":
            sprite.draw()
        else:
            sprite.draw()

        filename = images[current][::-1]
        filename = filename[:filename.find("\\")]
        filename = filename[::-1]
        viewer.set_caption("VIEWER: " + filename + " (image " + str(current + 1) + " out of " + str(len(images)) + ")")


    @viewer.event
    def on_key_press(symbol, modifiers):
        global sprite
        global current
        global images
        global player
        global first_played
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

        elif symbol == key.ENTER:
            if images[current][images[current].find("."):] == ".webm":
                source = pyglet.media.load(images[current])
                start_video(source)

        if symbol == key.UP or symbol == key.DOWN or symbol == key.LEFT or symbol == key.RIGHT:
            queue_image()

            if symbol == key.LEFT or symbol == key.RIGHT:
                sprite.scale = (screen_size[1] / sprite.image.height) - ((screen_size[1] / sprite.image.height) / 15)
                viewer.set_size(sprite.width, sprite.height)
                sprite.x = 0
                sprite.y = 0


    @viewer.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        if buttons == 1:
            ## If only left-mouse buttons held down...
            global sprite
            sprite.x += dx
            sprite.y += dy


    @viewer.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        global sprite
        if scroll_y == 1:
            ## Scrolled up
            sprite.scale += 0.125
            viewer.set_size(sprite.width, sprite.height)
        elif scroll_y == -1:
            ## Scrolled down
            sprite.scale -= 0.125
            viewer.set_size(sprite.width, sprite.height)

    @viewer.event
    def on_mouse_press(x, y, button, modifiers):
        global current
        if button == 4:
            ## If right clicked...
            if x < 20:
                ## Move back one...
                current -= 1
                if current < 0:
                    current = len(images) - 1
                queue_image()

            elif (viewer.width - x) < 20:
                ## Move forward one...
                current += 1
                if current > len(images) - 1:
                    current = 0
                queue_image()

    pyglet.app.run()
