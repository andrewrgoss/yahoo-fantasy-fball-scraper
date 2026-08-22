#!/usr/bin/python3
__author__ = 'agoss'

import argparse
import csv
import getpass
import os
from pathlib import Path
import time
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

import helper


def parse_args():
    parser = argparse.ArgumentParser(description="Yahoo Fantasy Football Scraper")
    parser.add_argument(
        "--yahoo-email", "--yahoo_email",
        dest="yahoo_email",
        default=os.getenv("YAHOO_EMAIL"),
        help="Yahoo email for login. If omitted, the CLI prompts for it.",
    )
    parser.add_argument(
        "--yahoo-password", "--yahoo_pw",
        dest="yahoo_password",
        default=os.getenv("YAHOO_PASSWORD"),
        help="Yahoo password. Omit this option to receive a hidden password prompt.",
    )
    parser.add_argument(
        "--yahoo-league-id", "--yahoo_league_id",
        dest="yahoo_league_id",
        default=os.getenv("YAHOO_LEAGUE_ID"),
        help="Yahoo league ID.",
    )
    parser.add_argument(
        "--yahoo-league-year", "--yahoo_league_year",
        dest="yahoo_league_year",
        default=os.getenv("YAHOO_LEAGUE_YEAR"),
        help="League year for projections.",
    )
    parser.add_argument(
        "--manual-login",
        action="store_true",
        help="Open Yahoo in the selected browser and let the user complete login manually.",
    )
    parser.add_argument(
        "--browser",
        choices=("safari", "chrome"),
        default=os.getenv("YAHOO_BROWSER", "safari").lower(),
        help="Browser controlled by Selenium (default: safari).",
    )
    parser.add_argument(
        "--output", "--output-file",
        dest="output_path",
        type=Path,
        help="Exact CSV output path. Defaults to a date-stamped file in the current directory.",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        type=Path,
        default=Path.cwd(),
        help="Directory for the default date-stamped CSV output.",
    )
    return parser.parse_args()


def resolve_arguments(args):
    """Resolve interactive values without putting a password in shell history."""

    if not args.yahoo_league_id:
        raise ValueError("A Yahoo league ID is required (use --yahoo-league-id).")
    if not args.yahoo_league_year:
        raise ValueError("A league year is required (use --yahoo-league-year).")
    if args.manual_login:
        return args
    if not args.yahoo_email:
        args.yahoo_email = input("Yahoo email: ").strip()
    if not args.yahoo_password:
        args.yahoo_password = getpass.getpass("Yahoo password: ")
    if not args.yahoo_email or not args.yahoo_password:
        raise ValueError("Yahoo email and password are required unless --manual-login is used.")
    return args


def resolve_output_path(args):
    """Return the requested output path and create its parent directory."""

    if args.output_path:
        output_path = args.output_path
    else:
        output_path = args.output_dir / (
            datetime.now().strftime("%Y_%m_%d_") + "yahoo_player_season_projections.csv"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def create_browser(browser_name):
    """Create the requested Selenium browser driver."""

    if browser_name == "chrome":
        return webdriver.Chrome()
    return webdriver.Safari()


def manual_yahoo_login(browser):
    """Open Yahoo and pause while the user completes login in the selected browser."""

    browser.get("https://login.yahoo.com")
    input("Complete Yahoo login in the browser, then press Enter here to continue: ")
    return browser


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
    args = resolve_arguments(parse_args())
    print("Program started\n**************START**************\n")

    # Output file
    csv_file = resolve_output_path(args)
    headers = [
        "PLAYER_NAME", "TEAM", "POSITION", "PLAYER_STATUS", "GP*", "BYE",
        "FANTASY_POINTS", "PRESEASON_RANKING", "ACTUAL_RANKING", "PCT_ROSTERED",
        "PASSING_YDS", "PASSING_TD", "PASSING_INT", "RUSHING_ATT", "RUSHING_YDS",
        "RUSHING_TD", "RECEPTIONS", "RECEIVING_YDS", "RECEIVING_TD", "TARGETS",
        "RET_TD", "2PT_CONVERSIONS", "FUMBLES_LOST",
    ]

    # Launch browser and login.
    browser = create_browser(args.browser)
    try:
        if args.manual_login:
            browser = manual_yahoo_login(browser)
        else:
            browser = helper.yahoo_account_login(args.yahoo_email, args.yahoo_password, browser)
        time.sleep(2)  # Allow the authenticated Yahoo page to settle.

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

        with csv_file.open("w", encoding="utf-8", newline="") as output_file:
            writer = csv.writer(output_file)
            writer.writerow(headers)

            for offset in range(0, 300, 25):
                browser.get(
                    f"https://football.fantasysports.yahoo.com/f1/{args.yahoo_league_id}/players"
                    f"?sort=PTS&sdir=1&status=A&pos=O&stat1=S_PS_{args.yahoo_league_year}&count={offset}"
                )
                try:
                    table = WebDriverWait(browser, 30).until(
                        expected_conditions.presence_of_element_located((By.CLASS_NAME, "Table"))
                    )
                except TimeoutException as exc:
                    raise RuntimeError(
                        "Yahoo player projection table was not found. Confirm that the browser is logged in "
                        "and that the league/year is available."
                    ) from exc

                rows = table.get_attribute("innerText").splitlines()
                rows = rows[39:]  # Skip headers.

                details, status, projections, step = [], "A", [], 0
                skipping_column_header = False
                for row in rows:
                    if row.startswith("Fan Pts"):
                        # Yahoo repeats the column header at every page offset.
                        details, status, projections, step = [], "A", [], 0
                        skipping_column_header = True
                        continue
                    if skipping_column_header:
                        if row == "":
                            skipping_column_header = False
                        continue
                    if not row.strip() or row in ("", ""):
                        if row == "" and details:
                            writer.writerow([*details, status, *projections])
                            details, status, projections, step = [], "A", [], 0
                        continue

                    if step == 0:  # Name + status.
                        name, status = parse_player_row(row, status_map)
                        details.append(name)
                    elif step == 1:  # Team + position.
                        team_position = row.split()
                        if len(team_position) >= 3:
                            team, pos = team_position[0], team_position[-1]
                            details.extend([team, pos])
                            print(f"{details[0]} - {pos} - {team}")
                        elif len(team_position) == 2:
                            team, pos = team_position
                            details.extend([team, pos])
                            print(f"{details[0]} - {pos} - {team}")
                        elif team_position:
                            # Current Yahoo markup places the position on the next line.
                            details.append(team_position[0])
                    elif step == 2 and len(details) == 2:  # Position on its own line.
                        pos = row.strip()
                        details.append(pos)
                        print(f"{details[0]} - {pos} - {details[1]}")
                    elif step > 3:  # Projections start after unused rows.
                        projections.append(row)
                    step += 1

                if details:  # Player record complete, write to file.
                    writer.writerow([*details, status, *projections])
    finally:
        browser.quit()

    print(f"CSV written to: {csv_file}")
    print(f"Program finished\n\n**************DONE**************\nTime elapsed: {time.time() - start:.2f}s\n")


if __name__ == "__main__":
    main()
