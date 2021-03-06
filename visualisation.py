'''
Produces images and video (using mencoder) from data from AI.
@author: null
'''
import Image, ImageDraw
import pickle
import subprocess

def drawFleet(draw, position, colour):
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

#where to save the images and video
saveFolder = "/home/null/temp/"
#where is the data from the AI
pickleDataPath = "/home/null/draw.pickle"  
#pickleDataPath = "draw.pickle"

    
def visualise():
    f = open(pickleDataPath)
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
        
        turnText = str(index)
        minimalNumberOfDigits = 3
        while len(turnText) < minimalNumberOfDigits:
            turnText = "0" + turnText
        
        draw.text((10, 10), "turn " + turnText + " planets left: " + str(len(data["neutralPlanets"])), white)
        draw.text((10, 25), "planets: " + str(len(data["myPlanets"])) + " fleets: " + str(len(data["myFleets"])), green)
        draw.text((10, 40), "planets: " + str(len(data["enemyPlanets"])) + " fleets: " + str(len(data["enemyFleets"])), red)
     
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
        
        
        filename = saveFolder + turnText + ".png"
        image1.save(filename)
    
    #convert to a video using mencoder
    command = "mencoder mf://" + saveFolder + "*.png -mf w=" + str(width) + ":h=" + str(height) + ":fps=1:type=png -ovc lavc -lavcopts vcodec=mpeg4 -oac copy -o /home/null/temp/video.mpg"
    subprocess.Popen(command.split(" "))

if __name__ == '__main__':
    visualise()
