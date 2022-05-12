import pygame as p
import pygame.gfxdraw as gfx
import math
from levels import levels
from playerblocks import *
import menu
"""
    glossary:
        globally used vars
        loadlevel - loads levels from levels.py (technically a var named levels in it)
        resetlevel - resets the current level (press R)
        convtoints - used for keyboard input and pygame.key
        calcinput - input processing, extending the main loop
        addblocks - add blocks to the player, in attached groups
        removeblocks - removes blocks from the player and puts them back into the world
        iscollision - checks if the player is colliding with something in the world (useful for movement)
         - includes blocks attached to the player
        calculategrav - extends the logic function,
         - runs at the end and drops the player 1 block per frame if they can ("gravity")
        logic - main logic/"controller" of the program, extends main loop
        render - render logic of game, runs after everything else per frame
        main loop - cotrols timing, runs calcinput, logic, render in that order
"""
# global variables -----------------------------------------------------------------------------------------------------
# initialize basic vars, start up pygame
p.init()
windowsize = (800, 600)
framerate = 60
tilesize = 30
frame = 0

# make window and clock
window = p.display.set_mode(windowsize)
clock = p.time.Clock()

mainmenu = menu.menu(window,levels)

# level storage
level = [[1]]
boxes = [[]]
lavacoords = []
# types of blocks that can be walked through
nocollide = [0, 4]

# drawing surface for rendering, is centered in render()
stage = p.Surface((len(level[0]) * tilesize, len(level) * tilesize))

# store where the finish (green) tile is
finishloc = [0, 0]

# what level we are currently in, as indicated in levels.py
currentlevel = 0

# player's current position
mainplayer = player()

# player direction movement along x axis
direction = 0

# player rotation, 1 = clockwise, -1 = counter-clockwise
rotdir = 0

# list of events used per frame
events = []

# check if the spacebar is being pressed
spacepressed = False

# remember if we are currently attached to something
attached = False

# rendered player position, is lerped constantly to current actual player position
renderplayer = player()

# max difference in position until the rendered player jumps into place, helps graphically
maxdifference = 0.1

# continue animation for several frames after death:
defaultdeathframes = 30
currentdeathframe = 0
dying = False
playeralivecolor = (0, 0, 255)
playerdeadcolor = (100, 100, 100)
renderrotdiff = 0
isrotating = False

images = {"playeroff":p.image.load("playeroff.png"),
          "playeron":p.image.load("playeron.png"),
          "boxon":p.image.load("boxon.png"),
          "boxoff":p.image.load("boxoff.png"),
          "wall":p.image.load("wall.png"),
          "empty":p.image.load("empty.png"),
          "lava":p.image.load("lava.png"),
          "playerdead":p.image.load("playerdead.png"),
          "finish":p.image.load("finish.png")}
resizedimages = {}



# mostly utility functions ---------------------------------------------------------------------------------------------
# this sets the level based on a list in levels.py
# levels are stored in a var named levels
# levels contains the list of every level
# each level consists of rows of strings
# each row is a row in the level
# each char in the row is a block, player position, finishing position, block, etc
# these are loaded to level var and blocks var (for movable blocks in the game)
def loadlevel(index):
    # utilize important variables
    global level
    global boxes
    global mainplayer
    global renderplayer
    global attached
    global stage
    global tilesize
    global finishloc
    global lavacoords
    global dying
    global currentdeathframe
    global renderrotdiff
    global isrotating


    # reset the player
    mainplayer = player([0, 0], [])
    attached = False
    dying = False
    currentdeathframe = 0
    renderrotdiff = 0
    isrotating = False


    # Block types
    # '#': solid : 1
    # ' ': empty : 0
    # 'p': player : 3
    # 'f': finish : 4
    # 'b': block : independent
    # 'l': lava : independent

    # process the level text list from levels.py to two multi-dimensional arrays
    leveltext = levels[index]
    output = []
    boxout = []
    lavaout = []
    for row in range(len(leveltext)):
        output.append([])
        boxout.append([])
        i = 0
        for block in leveltext[row]:
            if block == '#':
                output[row].append(1)
            elif block == 'p':
                mainplayer.setplayer([i, row])
                renderplayer.setplayer([i, row])
                output[row].append(0)
            elif block == 'f':
                output[row].append(4)
                finishloc = [i, row]
            elif block == 'l':
                lavaout.append([i, row])
                output[row].append(0)
            else:
                output[row].append(0)

            if block == 'b':
                boxout[row].append(1)
            else:
                boxout[row].append(0)
            i += 1

    # set the level and blocks into place
    level = output
    boxes = boxout
    lavacoords = lavaout
    # reset the tile size for rendering to something that will fit the screen
    tilesize = int(min(window.get_width() / len(level[0]), window.get_height() / len(level)))
    # reset the stage to a new surface(not sure why I put this here
    stage = p.Surface((len(level[0]) * tilesize, len(level) * tilesize))
    resizeall()


# just another way to run loadlevel with the current level
def resetlevel():
    loadlevel(currentlevel)


# a function which converts a list of boolean values to a list of ints at the indices where the input list is true
# used for pygame.key.get_pressed()
def convtoints(boollist):
    intlist = []
    for i in range(len(boollist)):
        if boollist[i]:
            intlist.append(i)
    return intlist


# function to add nearby blocks to a player, which is here because it can interact with the level
def addblocks(pos):
    # check that we at least have some available boxes nearby
    sumbl = boxes[pos[1] + 1][pos[0]] + boxes[pos[1] - 1][pos[0]] + boxes[pos[1]][pos[0] + 1] + boxes[pos[1]][
        pos[0] - 1]
    if sumbl == 0:
        return False
    # if there is a nearby box, add it to the player, remove it from the world,
    #  and check if there are any more boxes near the one selected (flood fill the boxes)
    if boxes[pos[1] + 1][pos[0]] == 1:
        mainplayer.addblock([pos[0], pos[1] + 1])
        boxes[pos[1] + 1][pos[0]] = 0
        addblocks([pos[0], pos[1] + 1])
    if boxes[pos[1] - 1][pos[0]] == 1:
        mainplayer.addblock([pos[0], pos[1] - 1])
        boxes[pos[1] - 1][pos[0]] = 0
        addblocks([pos[0], pos[1] - 1])
    if boxes[pos[1]][pos[0] + 1] == 1:
        mainplayer.addblock([pos[0] + 1, pos[1]])
        boxes[pos[1]][pos[0] + 1] = 0
        addblocks([pos[0] + 1, pos[1]])
    if boxes[pos[1]][pos[0] - 1] == 1:
        mainplayer.addblock([pos[0] - 1, pos[1]])
        boxes[pos[1]][pos[0] - 1] = 0
        addblocks([pos[0] - 1, pos[1]])
    # this also returns false or true if there were nearby boxes
    return True


# removes all blocks from the player, and places them back into the world
def removeblocks():
    global mainplayer
    global boxes
    for box in mainplayer.playerblocks:
        boxes[box[1] + mainplayer.playerpos[1]][box[0] + mainplayer.playerpos[0]] = 1
    mainplayer.playerblocks = []


# detect collision for player and blocks
# returns false if all is clear
def iscollision(playerent=player()):
    playercoord = getsafe(level, [playerent.playerpos[1], playerent.playerpos[0]])
    playerblock = getsafe(boxes, [playerent.playerpos[1], playerent.playerpos[0]])
    if playercoord not in nocollide or playerblock == 1:
        return True
    for block in playerent.playerblocks:
        if getsafe(level, [block[1] + playerent.playerpos[1], block[0] + playerent.playerpos[0]]) not in nocollide or \
                        getsafe(boxes, [block[1] + playerent.playerpos[1], block[0] + playerent.playerpos[0]]) == 1:
            return True
    return False


# check if the player can fall one block, and does so (only on player block and attached blocks)
def calculategrav():
    global mainplayer
    global level
    global boxes
    nextplayer = player([mainplayer.playerpos[0], mainplayer.playerpos[1] + 1], mainplayer.playerblocks)
    colliding = iscollision(nextplayer)
    if not colliding:
        mainplayer = nextplayer


# makes sure that the index that we are getting from this multidimensional array is a valid point, else it returns 0
def getsafe(array, position):
    if position[0] >= len(array) or position[1] >= len(array[0]):
        return 0
    else:
        return array[position[0]][position[1]]

# resizes all of the used sprites for rendering
def resizeall():
    global images
    global resizedimages
    for k, v in images.items():
        resizedimages[k] = p.transform.scale(v,(tilesize,tilesize))

# game loop functions --------------------------------------------------------------------------------------------------
# function that processes input
def calcinput():
    # get important variables from global
    global direction
    global events
    global spacepressed
    global rotdir

    # reset the direction and rotation we are moving, and spacebar being pressed
    direction = 0
    rotdir = 0
    spacepressed = False

    # disable controls if we are dead
    if dying:
        return
    # main event checker, sets values for above according to which buttons are being pressed
    for event in events:
        if event.type == p.KEYDOWN:
            # prints the key pressed, useful for finding key numbers
            print("key " + str(event.key) + " pressed")
            if event.key == 276:  # left arrow
                direction = -1
            elif event.key == 275:  # right arrow
                direction = 1
            elif event.key == 32:  # spacebar
                spacepressed = True
            elif event.key == 100:  # d key
                rotdir = 1
            elif event.key == 97:  # a key
                rotdir = -1
            elif event.key == 114:  # r key, resets level
                resetlevel()


# processes all of the math logic and whatnot, is called by main game loop
def logic():
    # get important vars
    global mainplayer
    global direction
    global attached
    global currentlevel
    global dying
    global currentdeathframe
    global renderrotdiff
    global isrotating
    # enable or disable (add or remove) attached blocks
    if spacepressed:
        if not attached:
            if addblocks(mainplayer.playerpos):
                attached = True
        else:
            removeblocks()
            attached = False
    # moves the player if they can and  if they want to
    if direction != 0:
        nextplayer = player([mainplayer.playerpos[0] + direction, mainplayer.playerpos[1]], mainplayer.playerblocks)
        moveable = not iscollision(nextplayer)
        if moveable:
            mainplayer.playerpos[0] += direction

    # rotates the player if they can and  if they want to
    if rotdir == 1:
        nextplayer = player([mainplayer.playerpos[0], mainplayer.playerpos[1]], mainplayer.playerblocks)
        nextplayer.rotatecw()
        moveable = not iscollision(nextplayer)
        if moveable:
            mainplayer = nextplayer
            renderrotdiff = -90

    elif rotdir == -1:
        nextplayer = player([mainplayer.playerpos[0], mainplayer.playerpos[1]], mainplayer.playerblocks)
        nextplayer.rotateccw()
        moveable = not iscollision(nextplayer)
        if moveable:
            mainplayer = nextplayer
            renderrotdiff = 90


    # check if the player can fall now
    calculategrav()

    # check if the player has beaten the level by now
    if mainplayer.playerpos == finishloc:
        currentlevel += 1
        if currentlevel == len(levels):
            pass
        else:
            loadlevel(currentlevel)

    if mainplayer.playerpos in lavacoords:
        dying = True
    if dying:
        currentdeathframe += 1
        if currentdeathframe >= defaultdeathframes:
            resetlevel()


# rendering, stuff is processed in order:
# static objects
# blocks
# player
def render():
    # vars
    global stage
    global window
    global isrotating
    global renderrotdiff
    # fill the background
    window.fill((0, 0, 0))
    stage.fill((0, 0, 0))
    for x in range(int(stage.get_width()/tilesize)):
        for y in range(int(stage.get_height()/tilesize)):
            stage.blit(resizedimages["empty"],(x*tilesize,y*tilesize))

    finishedrotating = False
    if renderrotdiff != 0:
        isrotating = True
        renderrotdiff /= 1.5
        if renderrotdiff < 5 and renderrotdiff > -5:
            renderrotdiff = 0
            isrotating = False
            finishedrotating = True

    #print(renderrotdiff)
    # update position and blocks of the rendered player
    if not isrotating:
        renderplayer.playerpos = [(renderplayer.playerpos[0] + mainplayer.playerpos[0]) / 2,
                              (renderplayer.playerpos[1] + mainplayer.playerpos[1]) / 2]
    if (abs(renderplayer.playerpos[0] - mainplayer.playerpos[0]) <= maxdifference
        and abs(renderplayer.playerpos[1] - mainplayer.playerpos[1]) <= maxdifference):
        renderplayer.playerpos = [mainplayer.playerpos[0], mainplayer.playerpos[1]]
    if not isrotating:
        renderplayer.playerblocks = mainplayer.playerblocks
    if finishedrotating:
        renderplayer.playerpos = mainplayer.playerpos



    # choose the color the player will be if dying
    if dying:
        playercolor = playerdeadcolor
    else:
        playercolor = playeralivecolor

    # render all static objects
    for lava in lavacoords:
        #gfx.box(stage,
        #        p.Rect(lava[0] * tilesize, lava[1] * tilesize,
        #               tilesize, tilesize), (255, 100, 0))
        stage.blit(resizedimages["lava"], [lava[0]*tilesize,lava[1]*tilesize])
    for row in range(len(level)):
        for bl in range(len(level[row])):
            if level[row][bl] == 1:
                #gfx.box(stage, p.Rect(bl * tilesize, row * tilesize, tilesize, tilesize), (255, 255, 255))
                stage.blit(resizedimages["wall"],[bl * tilesize, row * tilesize])
            if level[row][bl] == 4:
                #gfx.box(stage, p.Rect(bl * tilesize, row * tilesize, tilesize, tilesize), (0, 255, 0))
                stage.blit(resizedimages["finish"], [bl * tilesize, row * tilesize])
            if boxes[row][bl] == 1:
                #gfx.box(stage, p.Rect(bl * tilesize, row * tilesize, tilesize, tilesize), (255, 0, 0))
                stage.blit(resizedimages["boxoff"], [bl * tilesize, row * tilesize])

    # render the player
    playersprite = p.Surface((renderplayer.getwidth() * tilesize, renderplayer.getheight() * tilesize),p.SRCALPHA)

    playersprite = playersprite.convert_alpha()
    playersprite.set_alpha(50)
    print(playersprite.get_alpha())
    plypos = renderplayer.getcorner()
    plypos = [-plypos[0], -plypos[1]]
    if attached:
        playersprite.blit(resizedimages["playeron"],(plypos[0] * tilesize, plypos[1] * tilesize))
    else:
        playersprite.blit(resizedimages["playeroff"], (plypos[0] * tilesize, plypos[1] * tilesize))
    if dying:
        playersprite.blit(resizedimages["playerdead"], (plypos[0] * tilesize, plypos[1] * tilesize))
    #gfx.box(playersprite,
    #        p.Rect(plypos[0] * tilesize, plypos[1] * tilesize, tilesize, tilesize),
    #        playercolor)
    for box in renderplayer.playerblocks:
        playersprite.blit(resizedimages["boxon"],((box[0] + plypos[0]) * tilesize, (box[1] + plypos[1]) * tilesize))
        #gfx.box(playersprite,
        #        p.Rect((box[0] + plypos[0]) * tilesize, (box[1] + plypos[1]) * tilesize, tilesize, tilesize),
        #        (255, 255, 0))
    corner = renderplayer.getcorner()
    plypos = [renderplayer.playerpos[0] + corner[0], renderplayer.playerpos[1] + corner[1]]
    if isrotating and renderrotdiff < 0:
        pivot = renderplayer.brcrnr()
        pivot = [renderplayer.playerpos[0] + pivot[0],renderplayer.playerpos[1] + pivot[1]]
        wid = renderplayer.getwidth()
        hei = renderplayer.getheight()
        plypos = [pivot[0] - wid * math.cos(math.radians(90+renderrotdiff)),pivot[1]-wid*math.sin(math.radians(90+renderrotdiff))-hei*math.cos(math.radians(90+renderrotdiff))]
        playersprite = p.transform.rotate(playersprite,-90-renderrotdiff)
        print(-90-renderrotdiff)
    if isrotating and renderrotdiff > 0:
        pivot = renderplayer.blcrnr()
        pivot = [renderplayer.playerpos[0] + pivot[0], renderplayer.playerpos[1] + pivot[1]]
        wid = renderplayer.getwidth()
        hei = renderplayer.getheight()
        plypos = [pivot[0] - hei * math.sin(math.radians(90-renderrotdiff)),
                  pivot[1] - hei * math.cos(math.radians(90-renderrotdiff)) - wid * math.sin(math.radians(90-renderrotdiff))]
        playersprite = p.transform.rotate(playersprite,90-renderrotdiff)
        print(renderrotdiff)



    stage.blit(playersprite, (plypos[0] * tilesize, plypos[1] * tilesize))

    # apply the render to the center of the window
    window.blit(stage, ((window.get_width() - stage.get_width()) / 2, (window.get_height() - stage.get_height()) / 2))


# main game loop while statement ---------------------------------------------------------------------------------------
# var for checking if we are closing the window
quitting = False
# load the first level from levels
loadlevel(currentlevel)
# main loop
while not quitting:
    # set all events
    events = p.event.get()
    # check that we are not quitting yet
    for e in events:
        if e.type == p.QUIT:
            quitting = True

    # run functions in order
    calcinput()
    logic()
    render()

    # flip graphics output
    p.display.flip()

    # wait unitl the frame is over
    clock.tick(framerate)
    frame += 1

# this is run if we quit, I don't know if it is needed
p.quit()
