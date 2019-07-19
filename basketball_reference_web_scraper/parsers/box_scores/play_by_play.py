import re
from lxml import html

from basketball_reference_web_scraper.data import Location


TIME_REGEX = "([0-9]+):([0-9]+)\.([0-9]+)"
SCORE_REGEX = "([0-9]+)-([0-9]+)"


def parse_time(time_str):
    time_tuple = re.search(TIME_REGEX, time_str.strip())
    if time_tuple:
        return float(time_tuple[1]) * 60 + float(time_tuple[2]) + float(time_tuple[3]) / 10
    else:
        return -1.0


def parse_play_by_plays(page):
    tree = html.fromstring(page)
    table = tree.xpath('//table[@id="pbp"]')
    quarter = 0
    result = []
    for row in table[0][1:]:
        if row[0].get("colspan") == "6":
            quarter += 1
        elif row[1].get("colspan") != "5" and row[0].get("aria-label") != "Time":
            result.append(parse_play_by_play(row, quarter))
    return result


def parse_play_by_play(row, quarter):
    score = re.search(SCORE_REGEX, row[3].text_content().strip())
    location = Location.HOME if row[1].text_content().strip() == "" else Location.AWAY
    return {
        "quarter": quarter,
        "timestamp": parse_time(row[0].text_content()),
        "side": str(location),
        "score_away": score[1],
        "score_home": score[2],
        "description": row[1].text_content().strip() if location == Location.AWAY else row[5].text_content().strip()
    }
