'''
Created on 20.7.2010

@author: null
'''
import Image, ImageDraw
import pickle
import subprocess

def drawPlanet(draw, position, colour):
    #a small rectangle
    size = 1
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
    
    for index, data in enumerate(drawData): 
        image1 = Image.new("RGB", (width, height), black)
        draw = ImageDraw.Draw(image1)
        
        draw.text((10, 10), "turn " + str(index + 1), white)
     
        for planet in data["myPlanets"]:
            drawPlanet(draw, planet, green)
        for planet in data["neutralPlanets"]:
            drawPlanet(draw, planet, white)
        for planet in data["enemyPlanets"]:
            drawPlanet(draw, planet, red)
         
        filename = "/home/null/temp/" + str(index) + ".png"
        image1.save(filename)
    
    #convert to a video using mencoder
    command = "mencoder mf:///home/null/temp/*.png -mf w=" + str(width) + ":h=" + str(height) + ":fps=3:type=png -ovc lavc -lavcopts vcodec=mpeg4 -oac copy -o /home/null/temp/video.mpg"
    subprocess.Popen(command.split(" "))
