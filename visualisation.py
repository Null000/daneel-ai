'''
Created on 20.7.2010

@author: null
'''
import Image, ImageDraw
import pickle
import subprocess

def drawFleet(draw,position,colour):
    #a small cross
    size = 2
    [x, y, z] = position
    #scale
    global scaleFactor
    x /= scaleFactor
    y /= scaleFactor
    global offsetX
    global offsetY
    x += offsetX
    y += offsetY
    
    draw.line([(x - size, y - size), (x + size, y + size)], colour)
    draw.line([(x - size, y + size), (x + size, y - size)], colour)

def drawPlanet(draw, position, colour):
    #a small rectangle
    size = 2
    [x, y, z] = position
    #scale
    global scaleFactor
    x /= scaleFactor
    y /= scaleFactor
    global offsetX
    global offsetY
    x += offsetX
    y += offsetY
    
    draw.line([(x - size, y - size), (x + size, y - size), (x + size, y + size), (x - size, y + size), (x - size, y - size)], colour)

scaleFactor = 17000000
offsetX = 400
offsetY = 300
if __name__ == '__main__':
    f = open("/home/null/draw.pickle")
    drawData = pickle.load(f)
        
    width = 800
    height = 600
    center = height // 2
    
    white = (255, 255, 255)
    black = (0, 0, 0)
    blue = (0, 0, 255)
    red = (255, 0, 0)
    green = (0, 128, 0)
    yellow = (0, 255, 0)
    
    for index, data in enumerate(drawData): 
        image1 = Image.new("RGB", (width, height), black)
        draw = ImageDraw.Draw(image1)
        
        turnText = str(index + 1)
        minimalNumberOfDigits = 3
        while len(turnText) < minimalNumberOfDigits:
            turnText = "0"+turnText
        
        draw.text((10, 10), "turn " + turnText, white)
     
        for planet in data["myPlanets"]:
            drawPlanet(draw, planet, green)
        for planet in data["neutralPlanets"]:
            drawPlanet(draw, planet, white)
        for planet in data["enemyPlanets"]:
            drawPlanet(draw, planet, red)
     
        for fleet in data["myFleets"]:
            drawFleet(draw, fleet, green)
        for fleet in data["enemyFleets"]:
            drawFleet(draw, fleet, red)
        
        
        filename = "/home/null/temp/" + turnText + ".png"
        image1.save(filename)
    
    #convert to a video using mencoder
    command = "mencoder mf:///home/null/temp/*.png -mf w=" + str(width) + ":h=" + str(height) + ":fps=1:type=png -ovc lavc -lavcopts vcodec=mpeg4 -oac copy -o /home/null/temp/video.mpg"
    subprocess.Popen(command.split(" "))
