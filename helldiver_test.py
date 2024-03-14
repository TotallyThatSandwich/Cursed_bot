import requests

response = requests.get("https://helldivers-2.fly.dev/api/801/planets")
if response.status_code == 200:
    planets = response.json()
    
    for i in planets:
        index = i["index"]
        status_response = requests.get(f"https://helldivers-2.fly.dev/api/801/planets/{index}/status")
        if response.status_code == 200:
            status = status_response.json()
            owner = status["owner"]

            print(owner)
else:
    print("Failed to fetch planets data" + str(response.status_code))