import json
import os
import webbrowser

from difPy import dif

search = dif(r"C:\Users\Ian\Desktop\Folders\Redbot\images")
jsonobj = json.dumps(search.result, indent=4)
with open("DupeFinder.json", "w") as f:
    f.write(jsonobj)
webbrowser.open("DupeFinder.json")
os.system("pause")
os.remove("DupeFinder.json")
