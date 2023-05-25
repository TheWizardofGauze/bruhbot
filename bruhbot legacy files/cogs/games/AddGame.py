import json
import msvcrt
import os

clear = lambda: os.system("cls")
while True:
    print("Select platform:\n[1] Steam\n[2] Origin\n[3] Ubisoft\n[4] Rockstar")
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b"1":
                cat = "Steam"
            elif key == b"2":
                cat = "Origin"
            elif key == b"3":
                cat = "Ubisoft"
            elif key == b"4":
                cat = "Rockstar"
            else:
                continue
            clear()
            while True:
                game = input("Enter game name: ")
                gkey = input("Enter game key: ")
                if game == "":
                    print("Name cannot be empty.")
                    continue
                elif gkey == "":
                    print("Key cannot be empty.")
                    continue
                else:
                    break
            with open("games.json", "r+") as f:
                data = json.load(f)
                data[cat][game] = {"key": gkey}
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
            print(f'Game "{game}" added with key "{gkey}"')
            break
