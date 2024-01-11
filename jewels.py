import time
import random
import sys
from collections import defaultdict
# from turtle import tracer

import pyautogui
import numpy as np
from PIL import ImageGrab, Image 
import cv2
import keyboard
import mouse

# Optimized for this game https://games.ca.zone.msn.com/gameplayer/gameplayerHTML.aspx?game=msjewel 
url = None
# CONFIG
usePreset = 'BejeweledHD'
# usePreset = None
# Adjust the number of rows and columns of the game here
numberOJewelsInARow = 8
numberOJewelsInAColumn = 8
# Relevant for some games where you need to find threes only. 
matchOnlyThrees= False
# Some games require you to drag the jewels/objects
draggingMode = True
# Adjust the speed of the bot by changing these values
durationBetweenInterations = 0.01
mouseClickDuration = 0.01
mouseMoveDuration = 0.02
mouseDragDuration = 0.03


# This will take the colors as it finds them on the position. Can be tricky for matching as if the rgb value is only off by one (which is usually the case for many images) the matching won't work anymore. 
autoColorStrictMode = True
# The range in which to go up or down with the rgb values
checkingRange = 40
# This will try to detect the colors as much as possible, and if it does not find them it will take the RGB value as it is. 
autoColorMode = True
# For this to work you need to adjust the screenshots of both corners (top left and bottom right) and replace them in the folder where the script is. 
autoDetectionOfGameArea = False
# This sets the offset where to start taking the colors from automatically. Should be enough for most cases. (it takes half of the distance between each section)
autoOffset = True
# Add an offset to catch the color somewhere in the middle of the jewel. Only is taken into account when autoOffset = False, only really neccessary, when you are detecting the game area automatically
offsetToStartLokkingForFirstRow = 70 
offsetToStartLokkingForFirstColumn = 60

# DEBUGGING
# This shows the area where the programm is looking for the game and gets the color values from. Notice the white pixels. That is actually the position where the color is taken from
showBoardScreenshot = False
# Prints out a numpy array with all the y and y positions of each jewel so it is easier to grasp what is going on and from where to wehre move a jewel
printCoordinatesArray = False
# Sometimes not all colors can be found
printAllColorsIncludingMissing = False
# to read pixels pisition and color on screen you can use this in a python3 session: 
# pyautogui.displayMousePosition()

presets = {
    'MicrosoftJewels': {
        "url": "https://games.ca.zone.msn.com/gameplayer/gameplayerHTML.aspx?game=msjewel",
        "numberOJewelsInARow": 8,
        "numberOJewelsInAColumn": 8,
        "draggingMode": False,
        "autoColorStrictMode": False,
        "autoColorMode": False,
        "autoOffset": False,
        "offsetToStartLokkingForFirstRow": 70,
        "offsetToStartLokkingForFirstColumn": 60,

    }, 
    'BejeweledHD': {
        "url": "https://arcadespot.com/game/bejeweled-hd/",
        "numberOJewelsInARow": 8,
        "numberOJewelsInAColumn": 8,
        "draggingMode": False,
        "autoColorStrictMode": True,
        "autoColorMode": True,
        "checkingRange": 55,
        "autoOffset": True,
        "durationBetweenInterations": 0.4,
        "mouseClickDuration": 0.2,
    }, 
    'BejeweledHDTime': {
        "url": "https://arcadespot.com/game/bejeweled-hd/",
        "numberOJewelsInARow": 8,
        "numberOJewelsInAColumn": 8,
        "draggingMode": False,
        "autoColorStrictMode": True,
        "autoColorMode": True,
        "checkingRange": 30,
        "durationBetweenInterations": 0.01,
        "mouseClickDuration": 0.01,
        "autoOffset": True,
    }, 
    'JewelMonsters': {
        "url": "https://www.match3games.com/game/Jewel+Monsters",
        "numberOJewelsInARow": 8,
        "numberOJewelsInAColumn": 8,
        "draggingMode": True,
        "autoColorStrictMode": True,
        "autoColorMode": True,
        "checkingRange": 65,
        "durationBetweenInterations": 0,
        "mouseClickDuration": 0.01,
        "autoOffset": True,
    }, 
    'CandyCrusher': {
        "url": "https://kizi.com/games/candy-crusher",
        "numberOJewelsInARow": 6, # starts with 6 but gets more
        "numberOJewelsInAColumn": 6,
        "draggingMode": False,
        "autoColorStrictMode": True,
        "autoColorMode": True,
        "checkingRange": 40,
        "durationBetweenInterations": 0.4,
        "mouseClickDuration": 0.1,
        "autoOffset": True,
    }, 
    'CandyCrush': {
        "url": "https://simple.game/play/candy-crush/",
        "numberOJewelsInARow": 7, # starts with 6 but gets more
        "numberOJewelsInAColumn": 7,
        "draggingMode": False,
        "autoColorStrictMode": True,
        "autoColorMode": True,
        "checkingRange": 40,
        "durationBetweenInterations": 0.4,
        "mouseClickDuration": 0.1,
        "autoOffset": True,
    }, 
    'CandyMatch3': {
        "url": "https://simple.game/play/candy-match-3/",
        "numberOJewelsInARow": 10,
        "numberOJewelsInAColumn": 6,
        "draggingMode": True,
        "autoColorStrictMode": True,
        "autoColorMode": True,
        "checkingRange": 40,
        "durationBetweenInterations": 0.4,
        "mouseClickDuration": 0.1,
        "autoOffset": True,
    }

    
}

if usePreset:
    preset = presets[usePreset]
    try:    
        numberOJewelsInARow = preset["numberOJewelsInARow"]
        numberOJewelsInAColumn = preset["numberOJewelsInAColumn"]
        draggingMode = preset["draggingMode"]
        autoColorStrictMode = preset["autoColorStrictMode"]
        autoColorMode = preset["autoColorMode"]
        autoOffset = preset["autoOffset"]
        offsetToStartLokkingForFirstRow = preset["offsetToStartLokkingForFirstRow"]
        offsetToStartLokkingForFirstColumn = preset["offsetToStartLokkingForFirstColumn"]
        checkingRange = preset["checkingRange"]
        durationBetweenInterations = preset["durationBetweenInterations"]
        mouseClickDuration = preset["mouseClickDuration"]
    except:
        print("Could not find a preset value.")


upperLeftCorner = None
lowerRightCorner = None
if autoDetectionOfGameArea:
    print("Trying to find the game area on the screen automatically.")
if autoDetectionOfGameArea:
    upperLeftCorner = pyautogui.locateCenterOnScreen("region_upper_left_corner.PNG", confidence=0.7, grayscale=True)
    lowerRightCorner = pyautogui.locateCenterOnScreen("region_lower_right_corner.PNG", confidence=0.9, grayscale=True)

if upperLeftCorner == None or lowerRightCorner == None:
    if autoDetectionOfGameArea:
        print("Could not find upper left corner automatically.\n(To make this work you need to redo the screenshots of both corners in the folder of this application.)\nSwitching to manual mode:")

    upperLeftCornerSelected = input("Position your mouse at the upper left corner of the game and press ENTER.")
    if upperLeftCornerSelected == '':  # hitting enter == ''  empty string
        upperLeftCorner = pyautogui.position()
        print("Upper Left Corner set to:", upperLeftCorner)
    
    lowerRightCornerSelected = input("Now position your mouse at the lower right corner of the game and press ENTER.")
    if lowerRightCornerSelected == '':  # hitting enter == ''  empty string
        lowerRightCorner = pyautogui.position()
        print("Lower Right Corner set to:", lowerRightCorner)
    

gameAreaWidth = lowerRightCorner.x - upperLeftCorner.x
gameAreaHeight = lowerRightCorner.y - upperLeftCorner.y
gameAreaStepsOfJewelsX = gameAreaWidth / numberOJewelsInARow
gameAreaStepsOfJewelsY = gameAreaHeight / numberOJewelsInAColumn

if autoOffset:
    offsetToStartLokkingForFirstRow = int(gameAreaWidth / (numberOJewelsInARow * 2))
    offsetToStartLokkingForFirstColumn = int(gameAreaHeight / (numberOJewelsInAColumn * 2))

print("upperLeftCorner", upperLeftCorner)
print("lowerRightCorner", lowerRightCorner)
print("gameAreaWidth", gameAreaWidth)
print("gameAreaHeight", gameAreaHeight)
print("gameAreaStepsOfJewelsX", gameAreaStepsOfJewelsX)
print("gameAreaStepsOfJewelsY", gameAreaStepsOfJewelsY)


bboxGameArea = bbox=(upperLeftCorner.x, upperLeftCorner.y, lowerRightCorner.x, lowerRightCorner.y)
debugImage = ImageGrab.grab(bboxGameArea)
debugImagePixels = debugImage.load() # The load function transforms the image into a list of pixels

def getImage():
    return ImageGrab.grab(bboxGameArea)

stateOfGridDict = defaultdict(list)
stateOfGridAll = []
debugStateOfGridColors = []
debugStateOfGridPositions = []
possibleMoves = defaultdict(list)
detectedColorList = []
moves = 0
colorFinding = set()

def getAdditionalColors(px):
    if px not in colorFinding:
        color = getColorSymbol(px)
        if color:
            colorFinding.add(color)
        else:
            colorFinding.add(px)

def approximateColor(px): 
    global checkingRange
    for i in range(len(detectedColorList)):
        detectedColor = detectedColorList[i]
        if (detectedColor[0] - checkingRange < px[0] < detectedColor[0] + checkingRange) and (detectedColor[1] - checkingRange < px[1] < detectedColor[1] + checkingRange) and (detectedColor[2] - checkingRange < px[2] < detectedColor[2] + checkingRange):
            #print("Same color detected, differences:", detectedColor[0]-px[0], detectedColor[1]-px[1],detectedColor[2]-px[2])
            # print (f'color matched {detectedColor[0]} {detectedColor[1]} {detectedColor[2]}')
            # return (f'color{i}')
            return i 
    #print("could not detect", px)
    detectedColorList.append(px)
    return px

def getColorSymbol(px):
    if autoColorStrictMode:
        return approximateColor(px)
    # Adjust these values if the colors can't be found or have changed, etc. 
    if (0 <= px[0] < 90) and (45 < px[1] < 130)  and (210 < px[2] <= 255):
        return "blue"
    if (150 < px[0] < 200) and (0 < px[1] < 35)  and (20 < px[2] < 70):
        return "red"
    if (0 < px[0] < 100) and (50 < px[1] < 255)  and (0 < px[2] < 140):
        return "green"
    if (150 < px[0] < 230) and (5 < px[1] < 95) and (140 < px[2] < 230):
        return "teal"
    if (200 < px[0] < 260) and (180 < px[1] < 260) and (0 <= px[2] < 120):
        return "yellow"
    if (150 < px[0] < 240) and (40 < px[1] < 120) and (0 <= px[2] < 120):
        return "orange"
    if (210 < px[0] < 256) and (200 < px[1] < 256) and (200 <= px[2] < 256):
        return "white"
    # print("Color not found: RGB", px)
    if autoColorMode: 
        return approximateColor(px)
    return None

def updateBoardView():
    # The "load" function transforms the image into a list of pixels (?)
    pixels = getImage().load()
    rowNumber = 0
    columnNumber = 0
    for y in range(offsetToStartLokkingForFirstRow, gameAreaHeight, int(gameAreaStepsOfJewelsX)): # loop through each row 
        rowDebug = []
        rowPos = []
        for x in range(offsetToStartLokkingForFirstColumn, gameAreaWidth, int(gameAreaStepsOfJewelsY)): # and each cell/column of this row
            color = pixels[x, y]
            rowDebug.append(getColorSymbol(color))
            jewelInformation = {"color": getColorSymbol(color), "x": columnNumber, "y": rowNumber, "screenX": x, "screenY": y}
                      
            stateOfGridDict[getColorSymbol(color)].append(jewelInformation)
            stateOfGridAll.append(jewelInformation)
            
            locationString = f'{str(columnNumber)}.{str(rowNumber)}'
            rowPos.append(locationString)
            
            debugImagePixels[x, y] = (255, 255, 255) # For debugging this is very handy as it shows the position where the pixel is taken from 
            
            columnNumber += 1
            getAdditionalColors(color)
        rowNumber += 1
        debugStateOfGridColors.append(rowDebug)
        debugStateOfGridPositions.append(rowPos)
        columnNumber = 0

def addXOffset(x):
    return x + upperLeftCorner.x 

def addYOffset(y):
    return y + upperLeftCorner.y 

def clickAt(x,y):
    pyautogui.click(addXOffset(x),addYOffset(y), duration=mouseClickDuration)

def moveMouseTo(x,y):
    pyautogui.moveTo(addXOffset(x),addYOffset(y), duration=mouseMoveDuration)

def dragMouseTo(x, y):
    pyautogui.dragTo(addXOffset(x),addYOffset(y), duration=mouseDragDuration)

def getJewelByPosition(x, y, jewels):
    for i in range(len(jewels)):
        if jewels[i]["x"] == x and jewels[i]["y"] == y:
            return jewels[i]
    return None

def findPatterns(currentJewel, sameColor):
    
    oneJewelBefore = getJewelByPosition(currentJewel["x"]-1, currentJewel["y"], sameColor)
    oneJewelAfter = getJewelByPosition(currentJewel["x"]+1, currentJewel["y"], sameColor)
    oneJewelAbove = getJewelByPosition(currentJewel["x"], currentJewel["y"]-1, sameColor)
    oneJewelBelow = getJewelByPosition(currentJewel["x"], currentJewel["y"]+1, sameColor)

    twoJewelAfter = getJewelByPosition(currentJewel["x"]+2, currentJewel["y"], sameColor)
    twoJewelBefore = getJewelByPosition(currentJewel["x"]-2, currentJewel["y"], sameColor)
    twoJewelAbove = getJewelByPosition(currentJewel["x"], currentJewel["y"]-2, sameColor)
    twoJewelBelow = getJewelByPosition(currentJewel["x"], currentJewel["y"]+2, sameColor)
    
    threeJewelAfter = getJewelByPosition(currentJewel["x"]+3, currentJewel["y"], sameColor)
    threeJewelBefore = getJewelByPosition(currentJewel["x"]-3, currentJewel["y"], sameColor)
    threeJewelAbove = getJewelByPosition(currentJewel["x"], currentJewel["y"]-3, sameColor)
    threeJewelBelow = getJewelByPosition(currentJewel["x"], currentJewel["y"]+3, sameColor)
    
    fourJewelAfter = getJewelByPosition(currentJewel["x"]+4, currentJewel["y"], sameColor)
    fourJewelBefore = getJewelByPosition(currentJewel["x"]-4, currentJewel["y"], sameColor)
    fourJewelAbove = getJewelByPosition(currentJewel["x"], currentJewel["y"]-4, sameColor)
    fourJewelBelow = getJewelByPosition(currentJewel["x"], currentJewel["y"]+4, sameColor)

    oneJewelBelowAndOneAfter = getJewelByPosition(currentJewel["x"]+1, currentJewel["y"]+1, sameColor)
    oneJewelBelowAndOneBefore = getJewelByPosition(currentJewel["x"]-1, currentJewel["y"]+1, sameColor)
    oneJewelAboveAndOneBefore = getJewelByPosition(currentJewel["x"]-1, currentJewel["y"]-1, sameColor)
    oneJewelAboveAndOneAfter = getJewelByPosition(currentJewel["x"]+1, currentJewel["y"]-1, sameColor)

    twoJewelBelowAndOneAfter = getJewelByPosition(currentJewel["x"]+1, currentJewel["y"]+2, sameColor)
    twoJewelBelowAndOneBefore = getJewelByPosition(currentJewel["x"]-1, currentJewel["y"]+2, sameColor)
    twoJewelAboveAndOneBefore = getJewelByPosition(currentJewel["x"]-1, currentJewel["y"]-2, sameColor)
    twoJewelAboveAndOneAfter = getJewelByPosition(currentJewel["x"]+1, currentJewel["y"]-2, sameColor)

    oneJewelBelowAndTwoAfter = getJewelByPosition(currentJewel["x"]+2, currentJewel["y"]+1, sameColor)
    oneJewelBelowAndTwoBefore = getJewelByPosition(currentJewel["x"]-2, currentJewel["y"]+1, sameColor)
    oneJewelAboveAndTwoBefore = getJewelByPosition(currentJewel["x"]-2, currentJewel["y"]-1, sameColor)
    oneJewelAboveAndTwoAfter = getJewelByPosition(currentJewel["x"]+2, currentJewel["y"]-1, sameColor)
    
    # 5

    #  ___O__
    #  ___X__  
    #  _O____
    #  ___O__
    #  ___O__
    if oneJewelAbove and oneJewelBelow and oneJewelBelowAndOneBefore and twoJewelBelow and threeJewelBelow:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"], currentJewel["y"]+1, stateOfGridAll)
        possibleMoves[5].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelBelowAndOneBefore["screenX"], "moveFromScreenY": oneJewelBelowAndOneBefore["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 5})

    #  ___O__
    #  ___X__  
    #  ____O_
    #  ___O__
    #  ___O__
    if oneJewelAbove and oneJewelBelow and oneJewelBelowAndOneAfter and twoJewelBelow and threeJewelBelow:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"], currentJewel["y"]+1, stateOfGridAll)
        possibleMoves[5].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelBelowAndOneAfter["screenX"], "moveFromScreenY": oneJewelBelowAndOneAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 5})

    #  _____O____  
    #  _O_X___O_O_
    if oneJewelBefore and oneJewelAboveAndOneAfter and twoJewelAfter and threeJewelAfter:
        #print("Found a match of", currentJewel["color"], "threeJewelAfter")
        jewelToMoveTo = getJewelByPosition(currentJewel["x"]+1, currentJewel["y"], stateOfGridAll)
        possibleMoves[5].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelAboveAndOneAfter["screenX"], "moveFromScreenY": oneJewelAboveAndOneAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 5})

    #  _O_X___O_O_
    #  _____O____  
    if oneJewelBefore and oneJewelBelowAndOneAfter and twoJewelAfter and threeJewelAfter:
        #print("Found a match of", currentJewel["color"], "threeJewelAfter")
        jewelToMoveTo = getJewelByPosition(currentJewel["x"]+1, currentJewel["y"], stateOfGridAll)
        possibleMoves[5].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelBelowAndOneAfter["screenX"], "moveFromScreenY": oneJewelBelowAndOneAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 5})

    #  __________  
    #  _____0____
    #  _____X____  
    #  _O_O___O__

    # toDo: add this pattern
    # same on the other side

    # 4
    #  ___O__  
    #  ____O_
    #  ___X__
    #  ___O__
    if twoJewelAbove and oneJewelAboveAndOneAfter and oneJewelBelow:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"], currentJewel["y"]-1, stateOfGridAll)
        possibleMoves[4].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelAboveAndOneAfter["screenX"], "moveFromScreenY": oneJewelAboveAndOneAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 4})

    #  ___O__  
    #  _O____
    #  ___X__
    #  ___O__
    if twoJewelAbove and oneJewelAboveAndOneBefore and oneJewelBelow:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"], currentJewel["y"]-1, stateOfGridAll)
        possibleMoves[4].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelAboveAndOneBefore["screenX"], "moveFromScreenY": oneJewelAboveAndOneBefore["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 4})

    #  ___O__
    #  ___X__  
    #  ____O_
    #  ___O__
    if oneJewelAbove and oneJewelBelowAndOneAfter and twoJewelBelow:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"], currentJewel["y"]+1, stateOfGridAll)
        possibleMoves[4].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelBelowAndOneAfter["screenX"], "moveFromScreenY": oneJewelBelowAndOneAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 4})

    #  ___O__
    #  ___X__  
    #  _O____
    #  ___O__    
    if oneJewelAbove and oneJewelBelowAndOneBefore and twoJewelBelow:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"], currentJewel["y"]+1, stateOfGridAll)
        possibleMoves[4].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelBelowAndOneBefore["screenX"], "moveFromScreenY": oneJewelBelowAndOneBefore["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 4})

    #  _O_X___O__
    #  _____O___  
    if oneJewelBefore and oneJewelBelowAndOneAfter and twoJewelAfter:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"]+1, currentJewel["y"], stateOfGridAll)
        possibleMoves[4].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelBelowAndOneAfter["screenX"], "moveFromScreenY": oneJewelBelowAndOneAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 4})
    
    #  _____O___  
    #  _O_X___O__
    if oneJewelBefore and oneJewelAboveAndOneAfter and twoJewelAfter:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"]+1, currentJewel["y"], stateOfGridAll)
        possibleMoves[4].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelAboveAndOneAfter["screenX"], "moveFromScreenY": oneJewelAboveAndOneAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 4})

    #  ___O______  
    #  _O___X_O__
    if twoJewelBefore and oneJewelAboveAndOneBefore and oneJewelAfter:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"]-1, currentJewel["y"], stateOfGridAll)
        possibleMoves[4].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelAboveAndOneBefore["screenX"], "moveFromScreenY": oneJewelAboveAndOneBefore["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 4})

      
    #  _O___X_O__
    #  ___O______ 
    if twoJewelBefore and oneJewelBelowAndOneBefore and oneJewelAfter:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"]-1, currentJewel["y"], stateOfGridAll)
        possibleMoves[4].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelBelowAndOneBefore["screenX"], "moveFromScreenY": oneJewelBelowAndOneBefore["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 4})


    # 3 
    # VERTICAL

    #  ___X__ 
    #  ___O__ 
    #  _O____
    if oneJewelBelow and twoJewelBelowAndOneBefore:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"], currentJewel["y"]+2, stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": twoJewelBelowAndOneBefore["screenX"], "moveFromScreenY": twoJewelBelowAndOneBefore["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

    #  __X___ 
    #  __O___ 
    #  ____O_ 
    if oneJewelBelow and twoJewelBelowAndOneAfter:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"], currentJewel["y"]+2, stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": twoJewelBelowAndOneAfter["screenX"], "moveFromScreenY": twoJewelBelowAndOneAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

    #  __X__ 
    #  __O__
    #  _____
    #  __O__ 
    if oneJewelBelow and threeJewelBelow:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"], currentJewel["y"]+2, stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": threeJewelBelow["screenX"], "moveFromScreenY": threeJewelBelow["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

    #  __O__
    #  _____
    #  __X__ 
    #  __O__
    if oneJewelBelow and twoJewelAbove:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"], currentJewel["y"]-1, stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": twoJewelAbove["screenX"], "moveFromScreenY": twoJewelAbove["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

    #  __X__
    #  ____O
    #  __O__
    if twoJewelBelow and oneJewelBelowAndOneAfter:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"], currentJewel["y"]+1, stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelBelowAndOneAfter["screenX"], "moveFromScreenY": oneJewelBelowAndOneAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

    #  __X__
    #  0____
    #  __O__
    if twoJewelBelow and oneJewelBelowAndOneBefore:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"], currentJewel["y"]+1, stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelBelowAndOneBefore["screenX"], "moveFromScreenY": oneJewelBelowAndOneBefore["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

    #  O____
    #  __X__
    #  __O__
    if oneJewelBelow and oneJewelAboveAndOneBefore:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"], currentJewel["y"]-1, stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelAboveAndOneBefore["screenX"], "moveFromScreenY": oneJewelAboveAndOneBefore["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

    #  ____O
    #  _X___
    #  _O___
    if oneJewelBelow and oneJewelAboveAndOneAfter:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"], currentJewel["y"]-1, stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelAboveAndOneAfter["screenX"], "moveFromScreenY": oneJewelAboveAndOneAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

    # HORZONTAL

    #  _X_O__
    #  _____O
    if oneJewelAfter and oneJewelBelowAndTwoAfter:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"]+2, currentJewel["y"], stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelBelowAndTwoAfter["screenX"], "moveFromScreenY": oneJewelBelowAndTwoAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

    #  _____O
    #  _X_O__
    if oneJewelAfter and oneJewelAboveAndTwoAfter:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"]+2, currentJewel["y"], stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelAboveAndTwoAfter["screenX"], "moveFromScreenY": oneJewelAboveAndTwoAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

    #  _X_O____0
    if oneJewelAfter and threeJewelAfter:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"]+2, currentJewel["y"], stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": threeJewelAfter["screenX"], "moveFromScreenY": threeJewelAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

    #  0___X_O__
    if oneJewelAfter and twoJewelBefore:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"]-1, currentJewel["y"], stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": twoJewelBefore["screenX"], "moveFromScreenY": twoJewelBefore["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

    #  0______
    #  __X_O__
    if oneJewelAfter and oneJewelAboveAndOneBefore:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"]-1, currentJewel["y"], stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelAboveAndOneBefore["screenX"], "moveFromScreenY": oneJewelAboveAndOneBefore["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

    #  __X_O__
    #  0______
    if oneJewelAfter and oneJewelBelowAndOneBefore:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"]-1, currentJewel["y"], stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelBelowAndOneBefore["screenX"], "moveFromScreenY": oneJewelBelowAndOneBefore["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

    #  ____O___
    #  _X_____O
    if oneJewelAboveAndOneAfter and twoJewelAfter:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"]+1, currentJewel["y"], stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelAboveAndOneAfter["screenX"], "moveFromScreenY": oneJewelAboveAndOneAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

    #  _X_____O
    #  ____O___
    if oneJewelBelowAndOneAfter and twoJewelAfter:
        jewelToMoveTo = getJewelByPosition(currentJewel["x"]+1, currentJewel["y"], stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelBelowAndOneAfter["screenX"], "moveFromScreenY": oneJewelBelowAndOneAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

def findMatches():
    for key, sameColor in stateOfGridDict.items() :
        for j in range(len(sameColor)):
            currentJewel = sameColor[j]
            if currentJewel["color"] == None:
                continue
            findPatterns(currentJewel, sameColor)

def selectHighestMove():
    global moves
    if 0 < len(possibleMoves[5]):
        print("Possible moves with 5:", len(possibleMoves[5]))
        print("Possible moves with 4:", len(possibleMoves[4]))
        print("Possible moves with 3:", len(possibleMoves[3]))
        selectedMove = random.choice(possibleMoves[5])
        clickAt(selectedMove['moveFromScreenX'], selectedMove['moveFromScreenY'])
        if draggingMode:
            dragMouseTo(selectedMove['moveToScreenX'], selectedMove['moveToScreenY'])
        else:
            clickAt(selectedMove['moveToScreenX'], selectedMove['moveToScreenY'])
        moves += 1
        return
    if 0 < len(possibleMoves[4]):
        print("Possible moves with 4:", len(possibleMoves[4]))
        print("Possible moves with 3:", len(possibleMoves[3]))
        selectedMove = random.choice(possibleMoves[4])
        clickAt(selectedMove['moveFromScreenX'], selectedMove['moveFromScreenY'])
        if draggingMode:
            dragMouseTo(selectedMove['moveToScreenX'], selectedMove['moveToScreenY'])
        else:
            clickAt(selectedMove['moveToScreenX'], selectedMove['moveToScreenY'])
        moves += 1
        return
    if 0 < len(possibleMoves[3]):
        print("Possible moves with 3:", len(possibleMoves[3]))
        # does a random selection get lower points on average?
        selectedMove = random.choice(possibleMoves[3])
        # selectedMove = possibleMoves[3][0] # get first
        # selectedMove = possibleMoves[3][-1] # get last
        clickAt(selectedMove['moveFromScreenX'], selectedMove['moveFromScreenY'])
        if draggingMode:
            dragMouseTo(selectedMove['moveToScreenX'], selectedMove['moveToScreenY'])
        else:
            clickAt(selectedMove['moveToScreenX'], selectedMove['moveToScreenY'])
        moves += 1
    else:
        print("Currently no possible moves.")

def matchThrees():
    global moves
    if 0 < len(possibleMoves[3]):
        print("Possible moves with 3:", len(possibleMoves[3]))
        selectedMove = random.choice(possibleMoves[3])
        clickAt(selectedMove['moveFromScreenX'], selectedMove['moveFromScreenY'])
        if draggingMode:
            dragMouseTo(selectedMove['moveToScreenX'], selectedMove['moveToScreenY'])
        else:
            clickAt(selectedMove['moveToScreenX'], selectedMove['moveToScreenY'])
        moves += 1

if showBoardScreenshot:
    updateBoardView()
    debugImage.show()

while True:
    k = cv2.waitKey(1) & 0xFF
    # press 'q' to exit
    if k == ord('q'):
        break
    if keyboard.is_pressed("q"):
        print("q pressed, ending loop")
        break
    updateBoardView()
    if printAllColorsIncludingMissing:
        print("These are all the colors, including the missing ones", colorFinding)
    if printCoordinatesArray:
        print(np.array(debugStateOfGridPositions))
    print(np.array(debugStateOfGridColors))
    print("Moves made so far:", moves)
    findMatches()
    if matchOnlyThrees:
        matchThrees()
    else:
        # print("")
        
        selectHighestMove()

    # To be ready for next iteration
    stateOfGrid = []
    debugStateOfGridColors = []
    stateOfGridDict = defaultdict(list)
    stateOfGridAll = []
    debugStateOfGridPositions = []
    possibleMoves = defaultdict(list)
    time.sleep(durationBetweenInterations)


# Highscores
# 15.06.2022: 10350 - end because of bug 
# 15.06.2022: 17230 - end because of bug 
# 15.06.2022: 11410 - end because of bug 
# AVERAGE: 12997
# bugfixing session
# 15.06.2022: 36260 - end because of two in a row and one down and two in a column and one two up not detected
# 15.06.2022: 12780 - end because of failing to detect combinations
# 15.06.2022: 12430 - end because of not recognizing color, because it was "glowing"
# 15.06.2022: 54450 - end because of failing to detect combinations
# 15.06.2022: 26480 - end because of failing to detect combinations
# 15.06.2022: 28110 - out of matches!! Yeah, I did it!! Wohoo!!
# 15.06.2022: 43960 - end because of failing to detect combinations
# 16.06.2022: 45160 - end because of failing to detect combinations
# 16.06.2022: 18340 - end because of failing to detect combinations
# 16.06.2022: 39430 - end because of failing to detect combinations
# Improving main finding, fising bugs
# 18.06.2022: 52880 - out of matches
# 18.06.2022: 42070 - out of matches
# 18.06.2022: 44590 - out of matches
# 19.06.2022: 95080 - out of matches
# 19.06.2022: 95440 - failure to detect color (after restart continued to 97600)
# 19.06.2022: 47530 - out of matches
# 19.06.2022: 126540 - out of matches
# 19.06.2022: 33880 - out of matches
# 19.06.2022: 59720 - failure to detect color 
# 19.06.2022: 44140 - out of matches
# Get the highest combination (added 4 and 5 combinations)
# 19.06.2022: 43350 - out of matches
# 19.06.2022: 44250 - out of matches
# 19.06.2022: 82750 - did not know about all color disappearing crystal
# 19.06.2022: 47820 - out of matches
# 19.06.2022: 86510 - out of matches
# 19.06.2022: 83110 - out of matches
# 19.06.2022: 15400 - did not know about all color disappearing crystal (afer help 53800)
# 19.06.2022: 60740 - out of matches - moves: 193
# 19.06.2022: 34350 - out of matches - moves: 154
# 19.06.2022: 102100 - out of matches - moves: 302 (was stuck for a while)
# 19.06.2022: 38520 - out of matches - moves: 176
# 19.06.2022: 19880 - out of matches - moves: 104
# 20.06.2022: 50530 - color not detected - moves: 186
# 19.06.2022: 44470 - out of matches - moves: 180
# 19.06.2022: 66870 - out of matches - moves: 204
# 19.06.2022: 47550 - out of matches - moves: 154


# Game this bot was made for:
# https://games.ca.zone.msn.com/gameplayer/gameplayerHTML.aspx?game=msjewel
# same as above, works pretty well https://kizi.com/games/microsoft-jewel 
# why you not working ?? https://www.1001games.com/puzzle/jewel-shuffle
# same as above, it should work better :/ 
# https://games.ca.zone.msn.com/gameplayer/gameplayerHTML.aspx?game=msjewelnew
# https://www.1001games.com/puzzle/jewels-blitz-5
# not at all https://www.1001games.com/match-3/candy-rain
# works acutally pretty well :D https://www.1001games.com/match-3/aquablitz
# not https://www.match3games.com/game/Bejeweled
# not really good https://arcadespot.com/game/bejeweled-hd/
# okayish https://www.match3games.com/game/Jewel+Monsters
# pretty well https://www.match3games.com/game/Flat+Jewels
# another clone https://keygames.com/game/flat-jewels-match-3/