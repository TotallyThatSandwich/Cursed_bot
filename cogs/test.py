import urllib.request
from PIL import Image, ImageChops, ImageDraw, ImageFont
import math

stats = {
    "SHZ HUANSTITION": {
        "team": "Red",
        "kills": 10,
        "deaths": 6,
        "assists": 4,
        "KDA": "10/6/4",
        "KDR": 1.6666666666666667,
        "ACS": 313.56,
        "ADR": 206.22,
        "DD": 48,
        "rank": "Diamond 2",
        "HS": "24.0%",
        "agent": "Phoenix",
        "tag": "anime",
        "agentPfp": "https://media.valorant-api.com/agents/eb93336a-449b-9c1b-0a54-a891f7921d69/displayicon.png"
    },
    "microwave": {
        "team": "Red",
        "kills": 14,
        "deaths": 3,
        "assists": 2,
        "KDA": "14/3/2",
        "KDR": 4.666666666666667,
        "ACS": 414.56,
        "ADR": 282.0,
        "DD": 191,
        "rank": "Platinum 1",
        "HS": "26.82926829268293%",
        "agent": "Reyna",
        "tag": "penus",
        "agentPfp": "https://media.valorant-api.com/agents/a3bfb853-43b2-7238-a4f1-ad90e9e46bcc/displayicon.png"
    },
    "bbyguh": {
        "team": "Red",
        "kills": 12,
        "deaths": 4,
        "assists": 3,
        "KDA": "12/4/3",
        "KDR": 3.0,
        "ACS": 359.44,
        "ADR": 241.11,
        "DD": 128,
        "rank": "Unrated",
        "HS": "29.03225806451613%",
        "agent": "Sage",
        "tag": "zaddy",
        "agentPfp": "https://media.valorant-api.com/agents/569fdd95-4d10-43ab-ca70-79becc718b46/displayicon.png"
    },
    "FishMan321": {
        "team": "Blue",
        "kills": 0,
        "deaths": 9,
        "assists": 6,
        "KDA": "0/9/6",
        "KDR": 0.0,
        "ACS": 67.78,
        "ADR": 71.0,
        "DD": -110,
        "rank": "Gold 3",
        "HS": "5.555555555555555%",
        "agent": "Phoenix",
        "tag": "69420",
        "agentPfp": "https://media.valorant-api.com/agents/eb93336a-449b-9c1b-0a54-a891f7921d69/displayicon.png"
    },
    "l4k5": {
        "team": "Blue",
        "kills": 5,
        "deaths": 8,
        "assists": 1,
        "KDA": "5/8/1",
        "KDR": 0.625,
        "ACS": 164.56,
        "ADR": 109.11,
        "DD": -39,
        "rank": "Platinum 2",
        "HS": "18.75%",
        "agent": "Omen",
        "tag": "9767",
        "agentPfp": "https://media.valorant-api.com/agents/8e253930-4c05-31dd-1b6c-968525494517/displayicon.png"
    },
    "fatneek": {
        "team": "Blue",
        "kills": 11,
        "deaths": 8,
        "assists": 0,
        "KDA": "11/8/0",
        "KDR": 1.375,
        "ACS": 361.89,
        "ADR": 208.33,
        "DD": 54,
        "rank": "Gold 1",
        "HS": "13.88888888888889%",
        "agent": "Iso",
        "tag": "3023",
        "agentPfp": "https://media.valorant-api.com/agents/0e38b510-41a8-5780-5e8f-568b2a4f2d6c/displayicon.png"
    },
    "lilb00tyhair": {
        "team": "Red",
        "kills": 4,
        "deaths": 6,
        "assists": 4,
        "KDA": "4/6/4",
        "KDR": 0.6666666666666666,
        "ACS": 112.22,
        "ADR": 74.56,
        "DD": -53,
        "rank": "Bronze 2",
        "HS": "25.0%",
        "agent": "Omen",
        "tag": "3567",
        "agentPfp": "https://media.valorant-api.com/agents/8e253930-4c05-31dd-1b6c-968525494517/displayicon.png"
    },
    "powder": {
        "team": "Blue",
        "kills": 4,
        "deaths": 9,
        "assists": 0,
        "KDA": "4/9/0",
        "KDR": 0.4444444444444444,
        "ACS": 150.11,
        "ADR": 91.33,
        "DD": -95,
        "rank": "Gold 1",
        "HS": "12.5%",
        "agent": "Chamber",
        "tag": "4000",
        "agentPfp": "https://media.valorant-api.com/agents/22697a3d-45bf-8dd7-4fec-84a9e28c69d7/displayicon.png"
    },
    "Kiryu Kazuma": {
        "team": "Blue",
        "kills": 7,
        "deaths": 9,
        "assists": 1,
        "KDA": "7/9/1",
        "KDR": 0.7777777777777778,
        "ACS": 213.11,
        "ADR": 146.89,
        "DD": -47,
        "rank": "Gold 1",
        "HS": "23.809523809523807%",
        "agent": "Reyna",
        "tag": "Winds",
        "agentPfp": "https://media.valorant-api.com/agents/a3bfb853-43b2-7238-a4f1-ad90e9e46bcc/displayicon.png"
    },
    "fmv": {
        "team": "Red",
        "kills": 3,
        "deaths": 8,
        "assists": 2,
        "KDA": "3/8/2",
        "KDR": 0.375,
        "ACS": 93.89,
        "ADR": 60.78,
        "DD": -82,
        "rank": "Bronze 3",
        "HS": "20.0%",
        "agent": "Raze",
        "tag": "lean",
        "agentPfp": "https://media.valorant-api.com/agents/f94c3b30-42be-e959-889c-5aa313dba261/displayicon.png"
    }
}

agentPfpLink = "https://media.valorant-api.com/agents/320b2a48-4d9b-a075-30f1-1f93a9b638fa/displayicon.png"

mapLoadScreens = {
    "Ascent": "https://static.wikia.nocookie.net/valorant/images/e/e7/Loading_Screen_Ascent.png/revision/latest?cb=20200607180020",
    "Breeze": "https://static.wikia.nocookie.net/valorant/images/1/10/Loading_Screen_Breeze.png/revision/latest",
    "Bind": "https://static.wikia.nocookie.net/valorant/images/2/23/Loading_Screen_Bind.png/revision/latest",
    "Haven": "https://static.wikia.nocookie.net/valorant/images/7/70/Loading_Screen_Haven.png/revision/latest?cb=20200620202335",
    "Split":"https://static.wikia.nocookie.net/valorant/images/d/d6/Loading_Screen_Split.png/revision/latest?cb=20230411161807",
    "Pearl":"https://static.wikia.nocookie.net/valorant/images/a/af/Loading_Screen_Pearl.png/revision/latest?cb=20220622132842",
    "Lotus": "https://static.wikia.nocookie.net/valorant/images/d/d0/Loading_Screen_Lotus.png/revision/latest?cb=20230106163526",
    "Fracture": "https://static.wikia.nocookie.net/valorant/images/f/fc/Loading_Screen_Fracture.png/revision/latest?cb=20210908143656", 
    "Sunset": "https://static.wikia.nocookie.net/valorant/images/5/5c/Loading_Screen_Sunset.png/revision/latest?cb=20230829125442",
    "Icebox": "https://static.wikia.nocookie.net/valorant/images/1/13/Loading_Screen_Icebox.png/revision/latest"
}

mapLink = mapLoadScreens["Ascent"]
urllib.request.urlretrieve(mapLink, "map.png")

img = Image.new('RGB', (600, 800), color = (6, 9, 23))
draw = ImageDraw.Draw(img)

fnt = ImageFont.truetype(font="../fonts/OpenSans-Regular.ttf", size=20)
boldfnt = ImageFont.truetype(font="../fonts/OpenSans-Bold.ttf", size=45)

def sortLowestToHighest(arr, stat):
    length = len(arr)

    for i in range(length):
        for j in range(0, length):
            print(str(i), str(j))
            print(f"i: {str(arr[i])} {str(stats[arr[i]]['ACS'])}, j: {str(arr[j])} {str(stats[arr[j]]['ACS'])}")
            
            if stats[arr[i]][stat] > stats[arr[j]][stat]:
                print(f"Swapping {arr[i]} with {arr[j]}")
                arr[i], arr[j] = arr[j], arr[i]
    
    return arr

#start by dividing characters into their teams, then sorting by ACS, then draw the characters in their respective teams, with their stats
red_team = []
blue_team = []
for i in stats:
    if stats[i]["team"] == "Red":
        red_team.append(i)
    else:
        blue_team.append(i)

print("\nred:" + str(red_team))
print("blue:" + str(blue_team))

blueTeamPlayerCount = len(blue_team)
redTeamPlayerCount = len(red_team)

blue_team = sortLowestToHighest(blue_team, "ACS")
red_team = sortLowestToHighest(red_team, "ACS")

print("\nred:" + str(red_team))
print("blue:" + str(blue_team))

#Draws the map image cropped on the top of the image
mapImage = Image.open("map.png")
mapImage = mapImage.resize([1200, 654])
mapImage = ImageChops.offset(mapImage, math.floor((mapImage.width)/2+100), math.floor((mapImage.height)/2+100))
mapImage = mapImage.crop((0,0, mapImage.width, 100))
img.paste(mapImage, (0,0))

# Draw the line dividing map image with stats
draw.line([(0,100),(img.width,100)], fill=(33,38,46), width=15)

# from left to right, label stats
# agentPfp, username:tag, rank, KDA, ACS, ADR, HS%, DD
draw.rectangle([(img.width, img.width), (666, img.width)],fill=(0,0,0), outline=(33, 38, 46))
draw.text((0+(img.width/2)-45, 110), "13-03", font=boldfnt, fill=(255,255,255))


img.show()
