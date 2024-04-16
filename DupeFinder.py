import json
from multiprocessing import freeze_support
import os
import webbrowser

import difPy


if __name__ == "__main__":
    freeze_support()
    dif = difPy.build("C:/Users/Ian/Desktop/Folders/Redbot/images")
    search = difPy.search(dif)
    jsonobj = json.dumps(search.result, indent=4)
    with open("DupeFinder.json", "w") as f:
        f.write(jsonobj)
    webbrowser.open("DupeFinder.json")
    os.system("pause")
    os.remove("DupeFinder.json")
