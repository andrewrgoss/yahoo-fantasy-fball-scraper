#!/usr/bin/python3
__author__ = 'agoss'

import argparse
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

import helper


def parse_args():
    parser = argparse.ArgumentParser(description="Yahoo Fantasy Football Scraper")
    parser.add_argument("--yahoo_email", required=True, help="Yahoo email for login")
    parser.add_argument("--yahoo_pw", required=True, help="Yahoo password for login")
    parser.add_argument("--yahoo_league_id", required=True, help="Yahoo league ID")
    parser.add_argument("--yahoo_league_year", required=True, help="League year for projections")
    return parser.parse_args()


def write_csv_row(filepath, details, status, projections):
    row = [*details, status, *projections]
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(",".join(row) + "\n")


def parse_player_row(row, status_map):
    """Extract player name and status from row text."""
    for status, splits in status_map.items():
        for s in splits:
            if s in row:
                return row.split(s, 1)[0], status
    for marker in ["Video Forecast", "New Player Note", "Player Note", "No new player Notes"]:
        if marker in row:
            return row.split(marker, 1)[0], "A"
    return row, "A"


def main():
    start = time.time()
    args = parse_args()
    print("Program started\n**************START**************\n")

    # Output file
    csv_file = f"{datetime.now():%Y_%m_%d_}yahoo_player_season_projections.csv"
    headers = (
        "PLAYER_NAME,TEAM,POSITION,PLAYER_STATUS,GP*,BYE,FANTASY_POINTS,PRESEASON_RANKING,ACTUAL_RANKING,"
        "PCT_ROSTERED,PASSING_YDS,PASSING_TD,PASSING_INT,RUSHING_ATT,RUSHING_YDS,RUSHING_TD,"
        "RECEPTIONS,RECEIVING_YDS,RECEIVING_TD,TARGETS,RET_TD,2PT_CONVERSIONS,FUMBLES_LOST\n"
    )
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write(headers)

    # Launch browser and login
    browser = webdriver.Safari()
    browser = helper.yahoo_account_login(args.yahoo_email, args.yahoo_pw, browser)
    time.sleep(5)  # Wait for login to complete

    print("Extracting Yahoo! fantasy football player season projections...")

    # Status mapping
    status_map = {
        "IR": ["IRVideo", "IRNew", "IRPlayer", "IRNo new"],
        "NFI-R": ["NFI-RVideo", "NFI-RNew", "NFI-RPlayer", "NFI-RNo new"],
        "NFI-A": ["NFI-AVideo", "NFI-ANew", "NFI-APlayer", "NFI-ANo new"],
        "O": ["OVideo", "ONew", "OPlayer", "ONo new"],
        "PUP": ["PUPVideo", "PUPNew", "PUPPlayer", "PUPNo new"],
        "PUP-P": ["PUP-PVideo", "PUP-PNew", "PUP-PPlayer", "PUP-PNo new"],
        "D": ["DVideo", "DNew", "DPlayer", "DNo new"],
        "NA": ["NAVideo", "NANew", "NAPlayer", "NANo new"],
        "P": ["PVideo", "PNew", "PPlayer", "PNo new"],
        "Q": ["QVideo", "QNew", "QPlayer", "QNo new"],
        "SUSP": ["SUSPVideo", "SUSPNew", "SUSPPlayer", "SUSPNo new"],
    }

    for offset in range(0, 300, 25):
        browser.get(
            f"https://football.fantasysports.yahoo.com/f1/{args.yahoo_league_id}/players"
            f"?sort=PTS&sdir=1&status=A&pos=O&stat1=S_PS_{args.yahoo_league_year}&count={offset}"
        )
        time.sleep(5)  # Wait for page to load

        rows = browser.find_elements(By.CLASS_NAME, "Table")[0].get_attribute("innerText").splitlines()
        rows = rows[39:]  # Skip headers

        details, status, projections, step = [], "A", [], 0
        for row in rows:
            if not row.strip() or row in ("", ""):
                if row == "" and details:
                    write_csv_row(csv_file, details, status, projections)
                    details, status, projections, step = [], "A", [], 0
                continue

            if step == 0:  # Name + status
                name, status = parse_player_row(row, status_map)
                details.append(name)
            elif step == 1:  # Team + position
                team, _, pos = row.split(" ")
                details.extend([team, pos])
                print(f"{details[0]} - {pos} - {team}")
            elif step > 3:  # Projections start after unused rows
                projections.append(row)
            step += 1

        if details:  # Player record complete, write to file
            write_csv_row(csv_file, details, status, projections)

    print(f"Program finished\n\n**************DONE**************\nTime elapsed: {time.time() - start:.2f}s\n")


if __name__ == "__main__":
    main()
