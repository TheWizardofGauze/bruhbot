import json

# with open("games.json") as f:
data = {}
with open("games.txt", "r") as g:
    for line in g:
        if line.startswith("-"):
            if "-STEAM-" in line:
                slice1 = 16
                slice2 = 18
                cat = "Steam"
                games = {}
                continue
            elif "-ROCKSTAR-" in line:
                slice1 = 19
                slice2 = 20
                cat = "Rockstar"
                games = {}
                continue
            elif "-ORIGIN-" in line:
                slice1 = 24
                slice2 = 25
                cat = "Origin"
                games = {}
                continue
        a = line[:slice1]
        b = line[slice2:].replace("\n", "")
        games[b] = {"key": a}
        data[cat] = games
json_data = json.dumps(data)
with open("games.json", "w") as f:
    json.dump(data, f, indent=4)
