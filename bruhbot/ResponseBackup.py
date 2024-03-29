from datetime import datetime
import os
import shutil


def run():
    cwd = os.path.dirname(__file__) + "\\"
    bd = cwd + "backups\\"
    today = datetime.today()
    files = ["responses.txt", "data.json"]
    cogfiles = ["names.json", "OPBR.json"]
    for file in files:
        src = cwd + file
        dst = f"{bd}{file}.backup[{today.strftime('%Y-%m-%d_%I-%M-%p')}]"  # YYYY-MM-DD + HH/MM (12 hour time)
        shutil.copyfile(src, dst)
        filelist = os.listdir(bd)
        if len(filelist) > 20:  # max 5 of each
            oldest = min(
                filelist, key=lambda f: os.path.getmtime("{}/{}".format(bd, f))
            )
            os.remove(bd + oldest)
    for file in cogfiles:
        src = f"{cwd}cogs\\{file.replace('.json','')}\\{file}"
        dst = f"{bd}{file}.backup[{today.strftime('%Y-%m-%d_%I-%M-%p')}]"  # YYYY-MM-DD + HH/MM (12 hour time)
        shutil.copyfile(src, dst)
        filelist = os.listdir(bd)
        if len(filelist) > 20:  # max 5 of each
            oldest = min(
                filelist, key=lambda f: os.path.getmtime("{}/{}".format(bd, f))
            )
            os.remove(bd + oldest)


if __name__ == "__main__":
    run()
