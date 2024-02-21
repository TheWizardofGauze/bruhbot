import js2py


def calculateTimes(func: str):
    js = js2py.eval_js(
        """
    function calculateTimes(result) {
        const seasons = ["winter", "spring", "summer", "autumn"]
        const winterStarts = new Date(Date.UTC(2018, 10, 8, 14, 30, 00))
        let now = new Date()
        let numberOfSeasonsPassed = Math.floor(Math.abs(
            (now - winterStarts) / (7 * 24 * 60 * 60 * 1000)
        ))
        let currentSeason = seasons[numberOfSeasonsPassed % 4]
        let nextSeason = seasons[(numberOfSeasonsPassed + 1) % 4]
        winterStarts.setDate(winterStarts.getDate() + ((numberOfSeasonsPassed + 1) * 7))
        let timeTilNextSeason = winterStarts - now
        let days = Math.floor(timeTilNextSeason / (24 * 60 * 60 * 1000))
        let hours = Math.floor((timeTilNextSeason / (60 * 60 * 1000)) - (days * 24))
        let minutes = Math.floor((timeTilNextSeason / (60 * 1000)) - (hours * 60) - (days * 24 * 60))
        let seconds = Math.floor((timeTilNextSeason / 1000) - (minutes * 60) - (hours * 60 * 60) - (days * 24 * 60 * 60))
        return result = [currentSeason, nextSeason, days.toString(), hours.toString(), minutes.toString(), seconds.toString()]
    }
    """
    )

    if func == "season":
        s1s2 = []
        for i, j in enumerate(js([])):
            s1s2.append(j)
        return s1s2[:2]
    elif func == "time":
        dhms = []
        for i, j in enumerate(js([])):
            dhms.append(j)
        return dhms[2:6]


def season():
    season = calculateTimes("season")
    return season


def time():
    def plural(num):
        return 0 if int(num) == 1 else 1

    times = calculateTimes("time")
    days = times[0]
    hours = times[1]
    minutes = times[2]
    seconds = times[3]
    plurals = [
        ["day", "days"],
        ["hour", "hours"],
        ["minute", "minutes"],
        ["second", "seconds"],
    ]
    time = f"{days} {plurals[0][plural(days)]}, {hours} {plurals[1][plural(hours)]}, {minutes} {plurals[2][plural(minutes)]}, {seconds} {plurals[3][plural(seconds)]}"
    return time


if __name__ == "__main__":
    season = season()
    time = time()
    print(season)
    print(time)
