from datetime import datetime
import os


logdir = os.path.dirname(__file__) + "\\logs\\"


def run(exception: str):
    exception = exception.replace("\n", r"\n")
    today = datetime.today()
    filename = f"ErrorLog {today.strftime('%Y-%m-%d')}.txt"  # YYYY-MM-DD
    if not os.path.isfile(logdir + filename):
        with open(logdir + filename, "w") as f:
            f.write(f"{today.strftime('%I:%M %p')} {str(exception)}\n")  # HH/MM (12 hour time)
            return
    with open(logdir + filename, "a") as f:
        f.write(f"\n{today.strftime('%I:%M %p')} {str(exception)}\n")


def clear():
    files = os.listdir(logdir)
    for file in files:
        os.remove(logdir + file)


def last():
    files = os.listdir(logdir)
    if files == []:
        return "No logs found."
    newest = max(files, key=lambda f: os.path.getmtime("{}/{}".format(logdir, f)))
    log = newest.replace(".txt", "")
    with open(logdir + newest) as f:
        for line in f:
            pass
        last = line
        last = last.replace(r"\n", "\n")
    time = last[:8]
    error = last[9:]
    return {"log": log, "time": time, "error": error}


if __name__ == "__main__":
    e = "This is a test"
    run(e)
    # clear()
    # last()
