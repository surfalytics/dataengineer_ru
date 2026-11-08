"""Генерирует учебные таблицы про студенческий американский футбол (benn.college_football_*).

Школы и конференции — реальные (сезон 2013). Игроки выдуманы.
Запуск: python3 generate_football.py <папка для CSV>
"""
import csv
import random
import sys
from pathlib import Path

FBS = "FBS (Division I-A Teams)"
FCS = "FCS (Division I-AA Teams)"

# school_name, full_school_name, conference, state, division
SCHOOLS = [
    ("Alabama", "University of Alabama", "Southeastern", "AL", FBS),
    ("Auburn", "Auburn University", "Southeastern", "AL", FBS),
    ("Florida", "University of Florida", "Southeastern", "FL", FBS),
    ("Georgia", "University of Georgia", "Southeastern", "GA", FBS),
    ("LSU", "Louisiana State University", "Southeastern", "LA", FBS),
    ("Texas A&M", "Texas A&M University", "Southeastern", "TX", FBS),
    ("Tennessee", "University of Tennessee", "Southeastern", "TN", FBS),
    ("Ole Miss", "University of Mississippi", "Southeastern", "MS", FBS),
    ("Ohio State", "Ohio State University", "Big Ten", "OH", FBS),
    ("Michigan", "University of Michigan", "Big Ten", "MI", FBS),
    ("Penn State", "Pennsylvania State University", "Big Ten", "PA", FBS),
    ("Wisconsin", "University of Wisconsin", "Big Ten", "WI", FBS),
    ("Nebraska", "University of Nebraska", "Big Ten", "NE", FBS),
    ("Iowa", "University of Iowa", "Big Ten", "IA", FBS),
    ("Northwestern", "Northwestern University", "Big Ten", "IL", FBS),
    ("Texas", "University of Texas", "Big 12", "TX", FBS),
    ("Oklahoma", "University of Oklahoma", "Big 12", "OK", FBS),
    ("Baylor", "Baylor University", "Big 12", "TX", FBS),
    ("TCU", "Texas Christian University", "Big 12", "TX", FBS),
    ("Kansas State", "Kansas State University", "Big 12", "KS", FBS),
    ("West Virginia", "West Virginia University", "Big 12", "WV", FBS),
    ("Oregon", "University of Oregon", "Pac-12", "OR", FBS),
    ("Stanford", "Stanford University", "Pac-12", "CA", FBS),
    ("USC", "University of Southern California", "Pac-12", "CA", FBS),
    ("UCLA", "University of California, Los Angeles", "Pac-12", "CA", FBS),
    ("Washington", "University of Washington", "Pac-12", "WA", FBS),
    ("Arizona State", "Arizona State University", "Pac-12", "AZ", FBS),
    ("California", "University of California, Berkeley", "Pac-12", "CA", FBS),
    ("Florida State", "Florida State University", "Atlantic Coast", "FL", FBS),
    ("Clemson", "Clemson University", "Atlantic Coast", "SC", FBS),
    ("Miami (FL)", "University of Miami", "Atlantic Coast", "FL", FBS),
    ("Virginia Tech", "Virginia Polytechnic Institute and State University", "Atlantic Coast", "VA", FBS),
    ("Georgia Tech", "Georgia Institute of Technology", "Atlantic Coast", "GA", FBS),
    ("North Carolina", "University of North Carolina", "Atlantic Coast", "NC", FBS),
    ("Duke", "Duke University", "Atlantic Coast", "NC", FBS),
    ("Louisville", "University of Louisville", "American Athletic", "KY", FBS),
    ("UCF", "University of Central Florida", "American Athletic", "FL", FBS),
    ("Cincinnati", "University of Cincinnati", "American Athletic", "OH", FBS),
    ("Houston", "University of Houston", "American Athletic", "TX", FBS),
    ("Boise State", "Boise State University", "Mountain West", "ID", FBS),
    ("Fresno State", "California State University, Fresno", "Mountain West", "CA", FBS),
    ("San Diego State", "San Diego State University", "Mountain West", "CA", FBS),
    ("Utah State", "Utah State University", "Mountain West", "UT", FBS),
    ("Northern Illinois", "Northern Illinois University", "Mid-American", "IL", FBS),
    ("Toledo", "University of Toledo", "Mid-American", "OH", FBS),
    ("Ball State", "Ball State University", "Mid-American", "IN", FBS),
    ("Marshall", "Marshall University", "Conference USA", "WV", FBS),
    ("Rice", "Rice University", "Conference USA", "TX", FBS),
    ("Louisiana-Lafayette", "University of Louisiana at Lafayette", "Sun Belt", "LA", FBS),
    ("Arkansas State", "Arkansas State University", "Sun Belt", "AR", FBS),
    ("Notre Dame", "University of Notre Dame", "FBS Independents", "IN", FBS),
    ("BYU", "Brigham Young University", "FBS Independents", "UT", FBS),
    ("Army", "United States Military Academy", "FBS Independents", "NY", FBS),
    ("North Dakota State", "North Dakota State University", "Missouri Valley", "ND", FCS),
    ("Northern Iowa", "University of Northern Iowa", "Missouri Valley", "IA", FCS),
    ("Montana", "University of Montana", "Big Sky", "MT", FCS),
    ("Eastern Washington", "Eastern Washington University", "Big Sky", "WA", FCS),
    ("Montana State", "Montana State University", "Big Sky", "MT", FCS),
    ("Villanova", "Villanova University", "Colonial", "PA", FCS),
    ("Delaware", "University of Delaware", "Colonial", "DE", FCS),
    ("William & Mary", "College of William & Mary", "Colonial", "VA", FCS),
    ("Harvard", "Harvard University", "Ivy League", "MA", FCS),
    ("Yale", "Yale University", "Ivy League", "CT", FCS),
    ("Princeton", "Princeton University", "Ivy League", "NJ", FCS),
    ("Furman", "Furman University", "Southern", "SC", FCS),
    ("Samford", "Samford University", "Southern", "AL", FCS),
    ("Sam Houston State", "Sam Houston State University", "Southland", "TX", FCS),
    ("McNeese State", "McNeese State University", "Southland", "LA", FCS),
    ("Jackson State", "Jackson State University", "Southwestern Athletic", "MS", FCS),
    ("Grambling State", "Grambling State University", "Southwestern Athletic", "LA", FCS),
    ("Bethune-Cookman", "Bethune-Cookman University", "Mid-Eastern Athletic", "FL", FCS),
    ("Fordham", "Fordham University", "Patriot League", "NY", FCS),
    ("Lehigh", "Lehigh University", "Patriot League", "PA", FCS),
]

STATES_NEAR = {
    "AL": ["AL", "GA", "FL", "MS", "TN"], "FL": ["FL", "GA", "AL"], "GA": ["GA", "FL", "SC", "AL"],
    "LA": ["LA", "TX", "MS"], "TX": ["TX", "LA", "OK"], "TN": ["TN", "GA", "KY", "AL"], "MS": ["MS", "LA", "AL"],
    "OH": ["OH", "PA", "MI"], "MI": ["MI", "OH", "IL"], "PA": ["PA", "NJ", "OH", "NY"], "WI": ["WI", "IL", "MN"],
    "NE": ["NE", "KS", "IA", "CO"], "IA": ["IA", "IL", "MN"], "IL": ["IL", "OH", "IN"], "OK": ["OK", "TX"],
    "KS": ["KS", "MO", "TX"], "WV": ["WV", "PA", "OH", "VA"], "OR": ["OR", "CA", "WA"], "CA": ["CA", "AZ", "NV"],
    "WA": ["WA", "CA", "OR"], "AZ": ["AZ", "CA", "TX"], "SC": ["SC", "NC", "GA"], "VA": ["VA", "MD", "NC"],
    "NC": ["NC", "VA", "SC"], "KY": ["KY", "OH", "TN"], "ID": ["ID", "CA", "WA", "UT"], "UT": ["UT", "CA", "AZ"],
    "IN": ["IN", "IL", "OH"], "AR": ["AR", "TX", "MO"], "NY": ["NY", "NJ", "PA"], "ND": ["ND", "MN", "SD"],
    "MT": ["MT", "WA", "ID"], "DE": ["DE", "PA", "NJ", "MD"], "MA": ["MA", "NY", "CA"], "CT": ["CT", "NY", "MA"],
    "NJ": ["NJ", "NY", "PA"],
}
ALL_STATES = sorted({s for v in STATES_NEAR.values() for s in v})

CITIES = {
    "AL": ["Birmingham", "Mobile", "Montgomery"], "FL": ["Miami", "Tampa", "Jacksonville", "Orlando"],
    "GA": ["Atlanta", "Savannah", "Macon", "Valdosta"], "LA": ["New Orleans", "Baton Rouge", "Shreveport"],
    "TX": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth"], "TN": ["Memphis", "Nashville", "Knoxville"],
    "MS": ["Jackson", "Hattiesburg"], "OH": ["Columbus", "Cleveland", "Cincinnati"], "MI": ["Detroit", "Lansing"],
    "PA": ["Pittsburgh", "Philadelphia", "Erie"], "WI": ["Milwaukee", "Madison"], "NE": ["Omaha", "Lincoln"],
    "IA": ["Des Moines", "Cedar Rapids"], "IL": ["Chicago", "Peoria"], "OK": ["Tulsa", "Oklahoma City"],
    "KS": ["Wichita", "Topeka"], "WV": ["Charleston", "Morgantown"], "OR": ["Portland", "Eugene"],
    "CA": ["Los Angeles", "San Diego", "Sacramento", "Fresno", "Oakland"], "WA": ["Seattle", "Tacoma", "Spokane"],
    "AZ": ["Phoenix", "Tucson"], "SC": ["Columbia", "Charleston"], "VA": ["Richmond", "Norfolk"],
    "NC": ["Charlotte", "Raleigh"], "KY": ["Louisville", "Lexington"], "ID": ["Boise"], "UT": ["Salt Lake City", "Provo"],
    "IN": ["Indianapolis", "Fort Wayne"], "AR": ["Little Rock"], "NY": ["Buffalo", "Rochester", "New York"],
    "ND": ["Fargo"], "MT": ["Billings", "Missoula"], "DE": ["Wilmington"], "MA": ["Boston"], "CT": ["Hartford"],
    "NJ": ["Newark", "Trenton"], "MN": ["Minneapolis"], "SD": ["Sioux Falls"], "MO": ["St. Louis", "Kansas City"],
    "CO": ["Denver"], "MD": ["Baltimore"], "NV": ["Las Vegas"],
}

FIRST = ("James John Robert Michael William David Chris Daniel Matthew Anthony Mark Josh Andrew Kevin Brian Tyler "
         "Jordan Brandon Justin Ryan Jacob Nick Eric Aaron Kyle Marcus Darius Jalen Devin Malik Isaiah Trey Cameron "
         "Derrick Terrell Jamal Andre Corey Austin Logan Hunter Cody Blake Mason Caleb Elijah Xavier Dante Zach").split()
LAST = ("Smith Johnson Williams Brown Jones Miller Davis Wilson Anderson Taylor Thomas Moore Jackson Martin Lee "
        "Thompson White Harris Clark Lewis Robinson Walker Young Allen King Wright Scott Green Baker Adams Nelson Hill "
        "Campbell Mitchell Roberts Carter Phillips Evans Turner Parker Collins Edwards Stewart Morris Murphy Cook "
        "Rogers Reed Bailey Bell Cooper Howard Ward Cox Richardson Wood Watson Brooks Bennett Gray James Hughes "
        "Price Sanders Myers Long Ross Foster Powell Jenkins Perry Russell Sullivan Butler Barnes Fisher Henderson").split()

# позиция: (доля, средний рост в дюймах, средний вес в фунтах)
POSITIONS = {
    "QB": (0.06, 75, 215), "RB": (0.08, 70, 205), "WR": (0.13, 73, 190), "TE": (0.06, 76, 245),
    "OL": (0.18, 77, 300), "DL": (0.14, 75, 280), "LB": (0.12, 73, 230), "DB": (0.17, 71, 190),
    "K": (0.03, 72, 190), "P": (0.03, 74, 200),
}


def main(out: Path) -> None:
    rnd = random.Random(2013)
    out.mkdir(parents=True, exist_ok=True)
    teams = []
    for i, (name, full, conf, state, div) in enumerate(SCHOOLS, start=1):
        url = "http://espn.go.com/college-football/team/roster/_/id/" + str(1000 + i)
        teams.append([div, conf, name, url, i])
    with open(out / "college_football_teams.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["division", "conference", "school_name", "roster_url", "id"])
        w.writerows(teams)

    players, pid = [], 0
    pos_names = list(POSITIONS)
    pos_weights = [POSITIONS[p][0] for p in pos_names]
    for name, full, conf, state, div in SCHOOLS:
        for _ in range(rnd.randint(80, 110)):
            pid += 1
            pos = rnd.choices(pos_names, pos_weights)[0]
            _, h, wgt = POSITIONS[pos]
            height = max(66, min(81, round(rnd.gauss(h, 2))))
            weight = max(160, min(360, round(rnd.gauss(wgt + (height - h) * 6, 14))))
            home_state = rnd.choice(STATES_NEAR[state]) if rnd.random() < 0.8 else rnd.choice(ALL_STATES)
            hometown = rnd.choice(CITIES.get(home_state, ["Springfield"]))
            year = rnd.choices(["FR", "SO", "JR", "SR"], [0.32, 0.26, 0.22, 0.20])[0]
            players.append([full, name, f"{rnd.choice(FIRST)} {rnd.choice(LAST)}", pos, height, weight, year,
                            hometown, home_state, pid])
    with open(out / "college_football_players.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["full_school_name", "school_name", "player_name", "position", "height", "weight", "year",
                    "hometown", "state", "id"])
        w.writerows(players)
    print(f"college_football_teams.csv: {len(teams)} rows\ncollege_football_players.csv: {len(players)} rows")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
