from PIL import Image, ImageDraw, ImageFont, ImageChops
import math
import os
import random
import urllib.request



urllib.request.urlretrieve("https://static.wikia.nocookie.net/valorant/images/7/70/Loading_Screen_Haven.png/revision/latest?cb=20200620202335", "map.png")
urllib.request.urlretrieve("https://media.valorant-api.com/agents/eb93336a-449b-9c1b-0a54-a891f7921d69/displayicon.png", "character.png")
def createUserStatsImage(map=None, agentPfp=None, userStats=None):
    img = Image.new('RGB', (1200, 350), color = (6, 9, 23))
    draw = ImageDraw.Draw(img)
    fontPath = os.path.abspath("Cursed_bot/fonts/")
    fnt = ImageFont.truetype(font=fontPath+"\OpenSans-Regular.ttf", size=20)
    boldfnt = ImageFont.truetype(font=fontPath+"\OpenSans-Bold.ttf", size=45)


    #Draws the map image cropped on the top of the image
    mapImage = Image.open("map.png")
    mapImage = mapImage.resize([1200, 676])
    mapImage = ImageChops.offset(mapImage, 0, math.floor((mapImage.height)/2+100))
    mapImage = mapImage.crop((0,0, mapImage.width, 100))
    img.paste(mapImage, (0,0))
    
    #Draw the line dividing map image with stats
    draw.line([(0,100),(img.width,100)], fill=(255,255,255), width=15)

    #Paste agent picture on the left side of the image
    agentProfilePicture = Image.open("character.png")
    agentProfilePicture = agentProfilePicture.resize([250,250])
    img.paste(agentProfilePicture, (0,108))

    #Place player stats on the right of the agent picture
    draw.rectangle([(agentProfilePicture.width + 10, img.width), (666, img.width)],fill=(0,0,0), outline=(33, 38, 46))
    draw.text((agentProfilePicture.width + 20, 110), "Ascent", fill=(255,255,255), font=boldfnt)
    #KDA
    draw.text((agentProfilePicture.width + 20, 190), "KDA", fill=(255,255,255), font=fnt)
    draw.text((agentProfilePicture.width + 70, 190), "12/2/1", fill=(255,255,255), font=fnt)
    #ADR
    draw.text((agentProfilePicture.width + 20, 220), "ADR", fill=(255,255,255), font=fnt)
    draw.text((agentProfilePicture.width + 70, 220), "200", fill=(255,255,255), font=fnt)
    #ACS
    draw.text((agentProfilePicture.width + 20, 250), "ACS", fill=(255,255,255), font=fnt)
    draw.text((agentProfilePicture.width + 70, 250), "300", fill=(255,255,255), font=fnt)


    img.show()
    os.remove("map.png")
    os.remove("character.png")

createUserStatsImage()