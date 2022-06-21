import time
import sys
from collections import defaultdict

import pyautogui
import numpy as np
from PIL import ImageGrab, Image 
import cv2
import keyboard
import mouse

# Game this bot was made for:
# https://games.ca.zone.msn.com/gameplayer/gameplayerHTML.aspx?game=msjewel

# CONFIG
durationBetweenInterations = 0.8
numberOJewelsInARow = 8
numberOJewelsInAColumn = 8
# we add an offset to catch the color somewhere in the middle of the jewel
offsetToStartLokkingForFirstRow = 70 
offsetToStartLokkingForFirstColumn = 60
# DEBUGGING
# Prints out a numpy array with all the y and y positions of each jewel so it is easier to grasp what is going on and from where to wehre move a jewel
printCoordinatesArray = False
# Sometimes not all colors can be found
printAllColorsIncludingMissing = False
showBoardScreenshot = False

# to read pixels pisition and color on screen you can use this in a python3 session: 
# pyautogui.displayMousePosition()



print("Trying to find the game area on the screen automatically.")
upperLeftCorner = pyautogui.locateCenterOnScreen("region_upper_left_corner.PNG", confidence=0.7, grayscale=True)
lowerRightCorner = pyautogui.locateCenterOnScreen("region_lower_right_corner.PNG", confidence=0.9, grayscale=True)

if upperLeftCorner == None:
    print("Could not find upper left corner automatically.\n(To make this work you need to redo the screenshots of both corners in the folder of this application.)")

    upperLeftCornerSelected = input("Switching to manual mode:\nPosition your mouse at the upper left corner of the game and press ENTER.")
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

print("upperLeftCorner", upperLeftCorner)
print("lowerRightCorner", lowerRightCorner)
print("gameAreaWidth", gameAreaWidth)
print("gameAreaHeight", gameAreaHeight)
print("gameAreaStepsOfJewelsX", gameAreaStepsOfJewelsX)
print("gameAreaStepsOfJewelsY", gameAreaStepsOfJewelsY)

# regionGameArea = pyautogui.locateOnScreen("region_playing_field.png", confidence=0.7, grayscale=True)

bboxGameArea = bbox=(upperLeftCorner.x, upperLeftCorner.y, lowerRightCorner.x, lowerRightCorner.y)
grabbedImage = ImageGrab.grab(bboxGameArea)

def getImage():
    return ImageGrab.grab(bboxGameArea)

# The load function transforms the image into a list of pixels
# pixels = grabbedImage.load()
# grabbedImage.save("test.png")
# Image.open("test.png").show()
# print(grabbedImage[4, 4])
# print("steplength {}", int(regionGameArea.width / 8))

stateOfGrid = []
stateOfGridDict = defaultdict(list)
stateOfGridAll = []
#{}
debugStateOfGridColors = []
debugStateOfGridPositions = []
possibleMoves = defaultdict(list)
moves = 0
colorFinding = set()

def getAdditionalColors(px):
    if px not in colorFinding:
        color = getColorSymbol(px)
        if color:
            colorFinding.add(color)
        else:
            colorFinding.add(px)

def getColorSymbol(px):
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
    print("Color not found: RGB", px)
    return None

def updateBoardView():
    # The "load" function transforms the image into a list of pixels (?)
    pixels = getImage().load()
    rowNumber = 0
    columnNumber = 0
    for y in range(offsetToStartLokkingForFirstRow, gameAreaHeight, int(gameAreaStepsOfJewelsX)): # loop through each row 
        rowDebug = []
        rowPos = []
        row = []
        for x in range(offsetToStartLokkingForFirstColumn, gameAreaWidth, int(gameAreaStepsOfJewelsY)): # and each cell/column of this row
            color = pixels[x, y]
            # print("Color", color, "in row", rowNumber, "and cell nr.", columnNumber, "I see this as", getColorSymbol(color))
            rowDebug.append(getColorSymbol(color))
            jewelInformationOld = [getColorSymbol(color), x, y, rowNumber, columnNumber]
            #location2 = " ".join(str(rowNumber), ".",str(columnNumber))
            locationString = f'{str(columnNumber)}.{str(rowNumber)}'
            jewelInformation = {"color": getColorSymbol(color), "x": columnNumber, "y": rowNumber, "screenX": x, "screenY": y}
            #jewelInformation = {"row": rowNumber, "column": columnNumber}
            
            row.append(jewelInformationOld)
            stateOfGridDict[getColorSymbol(color)].append(jewelInformation)
            stateOfGridAll.append(jewelInformation)
            # For debugging this come in very handy as it shows the position where the pixel is taken from 
            # 
            pixels[x, y] = (255, 255, 255)
            columnNumber += 1
            getAdditionalColors(color)
            rowPos.append(locationString)
        rowNumber += 1
        stateOfGrid.append(row)
        debugStateOfGridColors.append(rowDebug)
        debugStateOfGridPositions.append(rowPos)
        columnNumber = 0

def addXOffset(x):
    return x + upperLeftCorner.x 

def addYOffset(y):
    return y + upperLeftCorner.y 

def clickAt(x,y):
    pyautogui.click(addXOffset(x),addYOffset(y), interval=0.2)

def moveMouseTo(x,y):
    pyautogui.moveTo(addXOffset(x),addYOffset(y), duration=0.1)

def findMatches():
    # print("Filter", stateOfGrid.filter(lambda: x))
    #for y in range(9):
    #    print("y", y)
    #for y in range(9):
    #    print("y2", y)
    #    for x in range(9):
    #        print("x,y3",y,x)
#    for y in range(0, len(stateOfGrid), 1):
#        for x in range(0, len(stateOfGrid[y]), 1):
    # ROW
    # stateOfGrid.reverse() # we want to start at the bottom
    #print("stateOfGrid",stateOfGrid)
    #print("stateOfGrid",np.array(stateOfGrid))
    #print("length", len(stateOfGrid))
    for y in range(8):
        # print(stateOfGrid[y])
    #for y in range(len(stateOfGrid)):
        #print("len(stateOfGrid)", len(stateOfGrid))
        # cell / column
        for x in range(8):            
        #for x in range(len(stateOfGrid[y])):
            try:
                #print("x:",x,"y",y)
                
                endOfGrid = len(stateOfGrid) - 1
                # Prevent being out of the grid with boundaries
                boundaryTop = 0 < y 
                #print("behind boundary" if not 0 < y  else "before bounudary")
                #print("behind boundary" if not y < endOfGrid else "before bounudary")
                boundaryTopPlusOne = 1 < y 
                boundaryTopPlusTwo = 2 < y 
                boundaryTopPlusThree = 3 < y 
                boundaryTopMinusTwo = 0 < y - 2
                boundaryRight = x < endOfGrid
                boundaryRightMinusTwo = x < endOfGrid - 2
                boundaryRightMinusThree = x < endOfGrid - 3
                boundaryLeft = 0 < x
                boundaryLeftPlusOne = 1 < x
                boundaryLeftPlusTwo = 2 < x
                boundaryBottom = y < endOfGrid
                boundaryBottomMinusTwo = y < endOfGrid - 1
                boundaryBottomMinusThree = y < endOfGrid - 2

                currentJewel = stateOfGrid[y][x]
                
                oneJewelBefore =   None if not boundaryLeft else stateOfGrid[y][x-1]
                oneJewelAfter =    None if not boundaryRight else stateOfGrid[y][x+1]
                oneJewelAbove =    None if not boundaryTop else stateOfGrid[y-1][x]
                oneJewelBelow =    None if not boundaryBottom else stateOfGrid[y+1][x]
                twoJewelBefore =   None if not boundaryLeftPlusOne else stateOfGrid[y][x-2]
                twoJewelAfter =    None if not boundaryRightMinusTwo else stateOfGrid[y][x+2]
                twoJewelAbove =    None if not boundaryTopPlusTwo else stateOfGrid[y-2][x]
                twoJewelBelow =    None if not boundaryBottomMinusTwo else stateOfGrid[y+2][x]
                threeJewelBefore = None if not boundaryLeftPlusTwo else  stateOfGrid[y][x-3]
                threeJewelAbove =  None if not boundaryTopMinusTwo else  stateOfGrid[y-3][x]
                #print("boundaryRightMinusThree",boundaryRightMinusThree)
                #print("boundaryRightMinusTwo",boundaryRightMinusTwo)
                #print("endOfGrid - 2=",endOfGrid - 2)
                #print("x+3=",x+3)
                #print("x + 3 - endOfGrid - 2=", x + 3 - endOfGrid - 2)
                
                #print("x + 3 - endOfGrid - 2 < 0 =", x + 3 - endOfGrid - 3 < 0)
                #print("before boundary" if boundaryRightMinusTwo else "behind bounudary")
                #print("behind boundary" if not boundaryRightMinusTwo else "before bounudary")
                #if boundaryRightMinusTwo:
                #    print("stateOfGrid[y][x+3]",stateOfGrid[y][x+3])
                #print(" ------ ")
                threeJewelAfter =  None if not boundaryRightMinusTwo else stateOfGrid[y][x+3]
                threeJewelBelow =  None if not boundaryBottomMinusThree else stateOfGrid[y+3][x]
                oneJewelBelowAndOneBefore =    None if not boundaryLeft or not boundaryBottom else stateOfGrid[y+1][x-1]
                oneJewelBelowAndOneAfter =     None if not boundaryRight or not boundaryTop else stateOfGrid[y+1][x+1]
                oneJewelAboveAndOneAfter =     None if not boundaryRight or not boundaryBottom else stateOfGrid[y-1][x+1]
                oneJewelAboveAndOneBefore =    None if not boundaryTop or not boundaryLeft else stateOfGrid[y-1][x-1]
                twoJewelBelowAndBefore =    None if not boundaryBottomMinusTwo or not boundaryLeftPlusOne else stateOfGrid[y+2][x-1]
                twoJewelBelowAndAfter =     None if not boundaryBottomMinusTwo or not boundaryRightMinusTwo else stateOfGrid[y+2][x+1]
                twoJewelAboveAndAfter =     None if not boundaryTopPlusTwo or not boundaryRightMinusTwo else stateOfGrid[y-2][x+1]
                twoJewelAboveAndBefore =    None if not boundaryTopPlusTwo or not boundaryLeftPlusOne else stateOfGrid[y-2][x-1]
                oneJewelBelowAndTwoBefore = None if not boundaryBottom or not boundaryLeftPlusTwo else stateOfGrid[y+1][x-2]
                oneJewelBelowAndTwoAfter =  None if not boundaryBottom or not boundaryRightMinusTwo else stateOfGrid[y+1][x+2]
                oneJewelAboveAndTwoAfter =  None if not boundaryBottomMinusTwo or not boundaryRightMinusTwo else stateOfGrid[y-1][x+2]
                oneJewelAboveAndTwoBefore = None if not boundaryBottomMinusTwo or not boundaryRightMinusTwo else stateOfGrid[y-1][x+2]
                    
            except IndexError as e:
                print("IndexError:", e)
                pass

            try: # I don0t want to fix all the bugs mode ...
                # print("x:",x,"y",y) 
                if currentJewel[0] == None:
                    #print("Found a None, continue")
                    continue

                # Enable automatic mouse movement for a nice viewing experience or debuggins 
                # moveMouseTo(currentJewel[1],currentJewel[2])

                #print("currentJewel[0]",currentJewel[0])
                #print("oneJewelBelow[0]",oneJewelBelow[0])
                #print("twoJewelBelowAndBefore[0]]",twoJewelBelowAndBefore[0])
                #print("twoJewelBelow[0]",twoJewelBelow[0])

                # VERTICAL
                
                #   this does not work, why??
                # not wprlmg: tiw vertical, one above and before
                # vertival two in one column and one below and after
                # horizpntaö two om a row woth one space between but one bloeww, same for vertical, both sides+
                # horizontal, tow in a row, then one space and one to the right, left also`???s`
                

                #  ___X__ 
                #  ___O__ 
                #  _O____ 
                if boundaryLeft and boundaryBottomMinusTwo: # avoid NoneType Errors and improve code readability (could also be in the if statement below)
                    if (currentJewel[0] == oneJewelBelow[0]) and (currentJewel[0] == twoJewelBelowAndBefore[0]):
                        print("Found a match of", currentJewel[0], "twoJewelBelowAndBefore")
                        clickAt(twoJewelBelowAndBefore[1], twoJewelBelowAndBefore[2])
                        clickAt(twoJewelBelow[1], twoJewelBelow[2])
                        return

                #  __X___ 
                #  __O___ 
                #  ____O_ 
                if boundaryRight and boundaryBottomMinusTwo:
                    if (currentJewel[0] == oneJewelBelow[0]) and (currentJewel[0] == twoJewelBelowAndAfter[0]):
                        print("Found a match of", currentJewel[0], "twoJewelBelowAndAfter")
                        clickAt(twoJewelBelowAndAfter[1], twoJewelBelowAndAfter[2])
                        clickAt(twoJewelBelow[1], twoJewelBelow[2])
                        return

                #  __X__ 
                #  __O__
                #  _____
                #  __O__ 
                if boundaryBottomMinusThree:
                    if (currentJewel[0] == oneJewelBelow[0]) and (currentJewel[0] == threeJewelBelow[0]):
                        print("Found a match of", currentJewel[0], "threeJewelBelow")
                        clickAt(threeJewelBelow[1], threeJewelBelow[2])
                        clickAt(twoJewelBelow[1], twoJewelBelow[2])
                        return

                #  __O__
                #  _____
                #  __X__ 
                #  __O__  
                if boundaryBottom and boundaryTopMinusTwo:
                    if (currentJewel[0] == oneJewelBelow[0]) and (currentJewel[0] == twoJewelAbove[0]):
                        print("Found a match of", currentJewel[0], "twoJewelAbove")
                        #print("y",y)
                        clickAt(twoJewelAbove[1], twoJewelAbove[2])
                        clickAt(oneJewelAbove[1], oneJewelAbove[2])
                        return

                #  __X__
                #  ____O
                #  __O__
                if boundaryRight and boundaryBottomMinusTwo:
                    if (currentJewel[0] == twoJewelBelow[0]) and (currentJewel[0] == oneJewelBelowAndOneAfter[0]):
                        print("Found a match of", currentJewel[0], "oneJewelBelowAndOneAfter vertical")
                        clickAt(oneJewelBelowAndOneAfter[1], oneJewelBelowAndOneAfter[2])
                        clickAt(oneJewelBelow[1], oneJewelBelow[2])
                        return

                #  __X__
                #  0____
                #  __O__
                if boundaryLeft and boundaryBottomMinusTwo:
                    if (currentJewel[0] == twoJewelBelow[0]) and (currentJewel[0] == oneJewelBelowAndOneBefore[0]):
                        print("Found a match of", currentJewel[0], "oneJewelBelowAndOneBefore vertical")
                        clickAt(oneJewelBelowAndOneBefore[1], oneJewelBelowAndOneBefore[2])
                        clickAt(oneJewelBelow[1], oneJewelBelow[2])
                        return

                #  O____
                #  __X__
                #  __O__
                if boundaryTop and boundaryLeft and boundaryBottom:
                    if (currentJewel[0] == oneJewelBelow[0]) and (currentJewel[0] == oneJewelAboveAndOneBefore[0]):
                        print("Found a match of", currentJewel[0], "oneJewelAboveAndOneBefore vertical")
                        clickAt(oneJewelAboveAndOneBefore[1], oneJewelAboveAndOneBefore[2])
                        clickAt(oneJewelAbove[1], oneJewelAbove[2])
                        return

                #  ____O
                #  _X___
                #  _O___
                if boundaryTop and boundaryRight and boundaryBottom:
                    if (currentJewel[0] == oneJewelBelow[0]) and (currentJewel[0] == oneJewelAboveAndOneAfter[0]):
                        print("Found a match of", currentJewel[0], "oneJewelAboveAndOneBefore vertical")
                        clickAt(oneJewelAboveAndOneAfter[1], oneJewelAboveAndOneAfter[2])
                        clickAt(oneJewelAbove[1], oneJewelAbove[2])
                        return


                # HORZONTAL   

                #  _X_O__
                #  _____O
                #print("x-2", x-2, "boundaryRightMinusTwo", boundaryRightMinusTwo, "endOfGrid - 1", endOfGrid - 1,"endOfGrid", endOfGrid)
                
                
                if boundaryRightMinusTwo and boundaryBottom:
                    #print("currentJewel[0]", currentJewel[0])
                    #print("oneJewelAfter[0]", oneJewelAfter[0])
                    #print("stateOfGrid[y+1][x+2]",stateOfGrid[y+1][x+2])
                    #print("stateOfGrid[y+1]",stateOfGrid[y+1])
                    #print("stateOfGrid[y+1][x+1]",stateOfGrid[y+1][x+1])
                    #print("oneJewelBelowAndTwoAfter[0]", oneJewelBelowAndTwoAfter[0])
                    if (currentJewel[0] == oneJewelAfter[0]) and (currentJewel[0] == oneJewelBelowAndTwoAfter[0]):
                        print("Found a match of", currentJewel[0], "oneJewelBelowAndTwoAfter")
                        clickAt(oneJewelBelowAndTwoAfter[1], oneJewelBelowAndTwoAfter[2])
                        clickAt(twoJewelAfter[1], twoJewelAfter[2])
                        return

                #  _____O
                #  _X_O__
                if boundaryRightMinusTwo and boundaryTop:
                    if (currentJewel[0] == oneJewelAfter[0]) and (currentJewel[0] == oneJewelAboveAndTwoAfter[0]):
                        print("Found a match of", currentJewel[0], "oneJewelAboveAndTwoAfter")
                        clickAt(oneJewelAboveAndTwoAfter[1], oneJewelAboveAndTwoAfter[2])
                        clickAt(twoJewelAfter[1], twoJewelAfter[2])
                        return

                #  _X_O____0
                if boundaryRightMinusThree:
                    if (currentJewel[0] == oneJewelAfter[0]) and (currentJewel[0] == threeJewelAfter[0]):
                        print("Found a match of", currentJewel[0], "threeJewelAfter")
                        clickAt(threeJewelAfter[1], threeJewelAfter[2])
                        clickAt(twoJewelAfter[1], twoJewelAfter[2])
                        return
                
                #  0___X_O__
                if boundaryLeftPlusTwo and boundaryRight:
                    if (currentJewel[0] == oneJewelAfter[0]) and (currentJewel[0] == twoJewelBefore[0]):
                        print("Found a match of", currentJewel[0], "twoJewelBefore")
                        clickAt(twoJewelBefore[1], twoJewelBefore[2])
                        clickAt(oneJewelBefore[1], oneJewelBefore[2])
                        return

                #  0______
                #  __X_O__
                if boundaryRight and boundaryLeft and boundaryTop:
                    if (currentJewel[0] == oneJewelAfter[0]) and (currentJewel[0] == stateOfGrid[y-1][x-1][0]):
                        print("Found a match of", currentJewel[0], "oneJewelAboveAndOneBefore horizontal")
                        print("currentJewel[0]",currentJewel[0])
                        print("oneJewelAfter[0]",oneJewelAfter[0])
                        print("oneJewelAboveAndOneBefore[0]]",oneJewelAboveAndOneBefore[0])
                        print("x-2", x-2, "boundaryRightMinusTwo", boundaryRightMinusTwo, "endOfGrid - 1", endOfGrid - 1,"endOfGrid", endOfGrid)
                        print("stateOfGrid[y-1][x-1]", stateOfGrid[y-1][x-1])
                        print("stateOfGrid[y-1]", stateOfGrid[y-1])
                        #print("twoJewelBelow[0]",twoJewelBelow[0])
                        clickAt( stateOfGrid[y-1][x-1][1],  stateOfGrid[y-1][x-1][2])
                        clickAt(oneJewelBefore[1], oneJewelBefore[2])
                        return

                #  __X_O__
                #  0______                
                if boundaryLeft and boundaryBottom and boundaryRight:
                    if (currentJewel[0] == oneJewelAfter[0]) and (currentJewel[0] == oneJewelBelowAndOneBefore[0]):
                        print("Found a match of", currentJewel[0], "oneJewelBelowAndOneBefore","this is jewel after:",oneJewelAfter[0])
                        clickAt(oneJewelBelowAndOneBefore[1], oneJewelBelowAndOneBefore[2])
                        clickAt(oneJewelBefore[1], oneJewelBefore[2])
                        return

                #  ____O___
                #  _X_____O
                if boundaryTop and boundaryRightMinusTwo:
                    if (currentJewel[0] == twoJewelAfter[0]) and (currentJewel[0] == oneJewelAboveAndOneAfter[0]):
                        print("Found a match of", currentJewel[0], "oneJewelAboveAndOneAfter")
                        clickAt(oneJewelAboveAndOneAfter[1], oneJewelAboveAndOneAfter[2])
                        clickAt(oneJewelAfter[1], oneJewelAfter[2])
                        return

                #  _X_____O
                #  ____O___
                if boundaryBottom and boundaryRightMinusTwo:
                    if (currentJewel[0] == twoJewelAfter[0]) and (currentJewel[0] == oneJewelBelowAndOneAfter[0]):
                        print("Found a match of", currentJewel[0], "oneJewelBelowAndOneAfter")
                        clickAt(oneJewelBelowAndOneAfter[1], oneJewelBelowAndOneAfter[2])
                        clickAt(oneJewelAfter[1], oneJewelAfter[2])
                        return
            except TypeError:
                #print(TypeError)
                #print("There is a type error, this means there is a bug somewhere, which I don't want to fix right now")
                pass

# updateBoardView()

# print (np.array(stateOfGrid))                

def getJewelByPosition(x, y, jewels):
    for i in range(len(jewels)):
        #print(jewels[i])
        if jewels[i]["x"] == x and jewels[i]["y"] == y:
            return jewels[i]
    return None

def findPatterns(currentJewel, sameColor):

    # {"color": getColorSymbol(color), "x": rowNumber, "y": columnNumber, "screenX": x, "screenY": y}
    
    #print("currentJewel", currentJewel)
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
        
    #print("oneJewelBefore", oneJewelBefore)

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
        #print(np.array(debugStateOfGridPositions))
        #print("current jewl", currentJewel)
        #print("one jewel below ", oneJewelBelow)
        #print("twoJewelBelowAndOneBefore",twoJewelBelowAndOneBefore)
        #print("jewelto move to", jewelToMoveTo,currentJewel["x"], currentJewel["y"]+2)
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
        #print("current", currentJewel)
        #print("oneJewelBelow", oneJewelBelow)
        #print("two below", twoJewelBelow)
        #print("threeJewelBelow",threeJewelBelow)
        #print("jewel to move to", jewelToMoveTo, currentJewel["color"], currentJewel["x"], currentJewel["y"]+2, currentJewel["y"]+2)
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
        #print("oneJewelBelowAndOneBefore",oneJewelBelowAndOneBefore)
        #print("jewelToMoveTo",jewelToMoveTo)
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
        #print("Found a match of", currentJewel["color"], "threeJewelAfter")
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
        #print("Found a match of", currentJewel["color"], "oneJewelBelowAndOneAfter")
        jewelToMoveTo = getJewelByPosition(currentJewel["x"]+1, currentJewel["y"], stateOfGridAll)
        possibleMoves[3].append({"color": currentJewel["color"], "moveFromScreenX": oneJewelBelowAndOneAfter["screenX"], "moveFromScreenY": oneJewelBelowAndOneAfter["screenY"], "moveToScreenX": jewelToMoveTo["screenX"], "moveToScreenY": jewelToMoveTo["screenY"], "value": 3})

def findMatchesImproved():
    #for colorIndex in stateOfGridDict:
    for key, sameColor in stateOfGridDict.items() :
        #
        #print(key)
        for j in range(len(sameColor)):
        #for j in value:
            #print("jewel:", sameColor[j])
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
        clickAt(possibleMoves[5][0]['moveFromScreenX'], possibleMoves[5][0]['moveFromScreenY'])
        clickAt(possibleMoves[5][0]['moveToScreenX'], possibleMoves[5][0]['moveToScreenY'])
        moves += 1
        return
    if 0 < len(possibleMoves[4]):
        print("Possible moves with 4:", len(possibleMoves[4]))
        print("Possible moves with 3:", len(possibleMoves[3]))
        clickAt(possibleMoves[4][0]['moveFromScreenX'], possibleMoves[4][0]['moveFromScreenY'])
        clickAt(possibleMoves[4][0]['moveToScreenX'], possibleMoves[4][0]['moveToScreenY'])
        moves += 1
        return
    if 0 < len(possibleMoves[3]):
        print("Possible moves with 3:", len(possibleMoves[3]))
        clickAt(possibleMoves[3][0]['moveFromScreenX'], possibleMoves[3][0]['moveFromScreenY'])
        clickAt(possibleMoves[3][0]['moveToScreenX'], possibleMoves[3][0]['moveToScreenY'])
        moves += 1
    else:
        print("Currently no possible moves.")

if showBoardScreenshot:
    grabbedImage.show()

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
    findMatchesImproved()
    selectHighestMove()

    # To be ready for next iteration
    stateOfGrid = []
    debugStateOfGridColors = []
    stateOfGridDict = defaultdict(list)
    stateOfGridAll = []
    debugStateOfGridPositions = []
    possibleMoves = defaultdict(list)
    #
    time.sleep(durationBetweenInterations)

# cv2.imshow('window',cv2.cvtColor(np.array(grabbedImage), cv2.COLOR_BGR2RGB))

# printscreen =  np.array(ImageGrab.grab(bbox=(regionGameArea.left, regionGameArea.top, regionGameArea.left + regionGameArea.width, regionGameArea.top + regionGameArea.height)))


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