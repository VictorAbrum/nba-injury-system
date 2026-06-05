from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.static import teams

import pandas as pd
import re


TEAM_SLUGS = {

    "hawks":
    "Atlanta Hawks",

    "celtics":
    "Boston Celtics",

    "nets":
    "Brooklyn Nets",

    "hornets":
    "Charlotte Hornets",

    "bulls":
    "Chicago Bulls",

    "cavaliers":
    "Cleveland Cavaliers",

    "mavs":
    "Dallas Mavericks",

    "nuggets":
    "Denver Nuggets",

    "pistons":
    "Detroit Pistons",

    "warriors":
    "Golden State Warriors",

    "rockets":
    "Houston Rockets",

    "pacers":
    "Indiana Pacers",

    "clippers":
    "Los Angeles Clippers",

    "lakers":
    "Los Angeles Lakers",

    "grizzlies":
    "Memphis Grizzlies",

    "heat":
    "Miami Heat",

    "bucks":
    "Milwaukee Bucks",

    "timberwolves":
    "Minnesota Timberwolves",

    "pelicans":
    "New Orleans Pelicans",

    "knicks":
    "New York Knicks",

    "thunder":
    "Oklahoma City Thunder",

    "magic":
    "Orlando Magic",

    "76ers":
    "Philadelphia 76ers",

    "suns":
    "Phoenix Suns",

    "blazers":
    "Portland Trail Blazers",

    "kings":
    "Sacramento Kings",

    "spurs":
    "San Antonio Spurs",

    "raptors":
    "Toronto Raptors",

    "jazz":
    "Utah Jazz",

    "wizards":
    "Washington Wizards"
}

TEAM_LOGOS = {

    "Atlanta Hawks":
    "https://cdn.nba.com/logos/nba/1610612737/primary/L/logo.svg",

    "Boston Celtics":
    "https://cdn.nba.com/logos/nba/1610612738/primary/L/logo.svg",

    "Brooklyn Nets":
    "https://cdn.nba.com/logos/nba/1610612751/primary/L/logo.svg",

    "Charlotte Hornets":
    "https://cdn.nba.com/logos/nba/1610612766/primary/L/logo.svg",

    "Chicago Bulls":
    "https://cdn.nba.com/logos/nba/1610612741/primary/L/logo.svg",

    "Cleveland Cavaliers":
    "https://cdn.nba.com/logos/nba/1610612739/primary/L/logo.svg",

    "Dallas Mavericks":
    "https://cdn.nba.com/logos/nba/1610612742/primary/L/logo.svg",

    "Denver Nuggets":
    "https://cdn.nba.com/logos/nba/1610612743/primary/L/logo.svg",

    "Detroit Pistons":
    "https://cdn.nba.com/logos/nba/1610612765/primary/L/logo.svg",

    "Golden State Warriors":
    "https://cdn.nba.com/logos/nba/1610612744/primary/L/logo.svg",

    "Houston Rockets":
    "https://cdn.nba.com/logos/nba/1610612745/primary/L/logo.svg",

    "Indiana Pacers":
    "https://cdn.nba.com/logos/nba/1610612754/primary/L/logo.svg",

    "Los Angeles Clippers":
    "https://cdn.nba.com/logos/nba/1610612746/primary/L/logo.svg",

    "Los Angeles Lakers":
    "https://cdn.nba.com/logos/nba/1610612747/primary/L/logo.svg",

    "Memphis Grizzlies":
    "https://cdn.nba.com/logos/nba/1610612763/primary/L/logo.svg",

    "Miami Heat":
    "https://cdn.nba.com/logos/nba/1610612748/primary/L/logo.svg",

    "Milwaukee Bucks":
    "https://cdn.nba.com/logos/nba/1610612749/primary/L/logo.svg",

    "Minnesota Timberwolves":
    "https://cdn.nba.com/logos/nba/1610612750/primary/L/logo.svg",

    "New Orleans Pelicans":
    "https://cdn.nba.com/logos/nba/1610612740/primary/L/logo.svg",

    "New York Knicks":
    "https://cdn.nba.com/logos/nba/1610612752/primary/L/logo.svg",

    "Oklahoma City Thunder":
    "https://cdn.nba.com/logos/nba/1610612760/primary/L/logo.svg",

    "Orlando Magic":
    "https://cdn.nba.com/logos/nba/1610612753/primary/L/logo.svg",

    "Philadelphia 76ers":
    "https://cdn.nba.com/logos/nba/1610612755/primary/L/logo.svg",

    "Phoenix Suns":
    "https://cdn.nba.com/logos/nba/1610612756/primary/L/logo.svg",

    "Portland Trail Blazers":
    "https://cdn.nba.com/logos/nba/1610612757/primary/L/logo.svg",

    "Sacramento Kings":
    "https://cdn.nba.com/logos/nba/1610612758/primary/L/logo.svg",

    "San Antonio Spurs":
    "https://cdn.nba.com/logos/nba/1610612759/primary/L/logo.svg",

    "Toronto Raptors":
    "https://cdn.nba.com/logos/nba/1610612761/primary/L/logo.svg",

    "Utah Jazz":
    "https://cdn.nba.com/logos/nba/1610612762/primary/L/logo.svg",

    "Washington Wizards":
    "https://cdn.nba.com/logos/nba/1610612764/primary/L/logo.svg"
}


def feet_inches_to_meters(height):

    try:

        feet, inches = map(
            int,
            height.split("-")
        )

        return round(

            (
                feet * 30.48
                +
                inches * 2.54
            ) / 100,

            2
        )

    except:

        return None


def pounds_to_kg(weight):

    try:

        return round(

            int(weight)
            * 0.453592,

            1
        )

    except:

        return None


def scrape_team(roster_url):

    slug_match = re.search(

        r'nba\.com/([^/]+)',

        roster_url
    )

    if not slug_match:

        raise Exception(
            "URL inválida."
        )

    slug = slug_match.group(1)

    if slug == "team":

        slug = re.search(

            r'nba\.com/([^/]+)/team',

            roster_url

        ).group(1)

    team_name = TEAM_SLUGS.get(slug)

    if not team_name:

        raise Exception(
            f"Time '{slug}' não reconhecido."
        )

    nba_teams = teams.get_teams()

    team = next(

        (
            t for t in nba_teams
            if t["full_name"]
            == team_name
        ),

        None
    )

    roster = commonteamroster.CommonTeamRoster(

        team_id=team["id"]
    )

    df = roster.get_data_frames()[0]

    jogadores = []

    for _, row in df.iterrows():

        player_id = row[
            "PLAYER_ID"
        ]

        jogadores.append({

            "jogador":
            row["PLAYER"],

            "time":
            team_name,

            "idade":
            25,

            "altura":

            feet_inches_to_meters(
                row["HEIGHT"]
            ),

            "peso":

            pounds_to_kg(
                row["WEIGHT"]
            ),

            "temporada":
            "2025-26",

            "jogos_temporada":
            0,

            "foto":

            f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png",

            "logo_time":

            TEAM_LOGOS.get(
                team_name,
                ""
            )
        })

    return pd.DataFrame(
        jogadores
    )


if __name__ == "__main__":

    df = scrape_team(

        "https://www.nba.com/lakers/team/roster-coaches"
    )

    print(df)

    print("\nTOTAL:")
    print(len(df))