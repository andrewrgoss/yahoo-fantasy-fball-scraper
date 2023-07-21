#!/usr/bin/python3
__author__ = 'agoss'

import argparse
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import time


def init_config():
    start = time.time()
    arg_list = get_arg_list()
    return start, arg_list


# Listing the arguments that can be passed in though the command line
def get_arg_list():
    parser = argparse.ArgumentParser(description='Parses command line arguments')
    parser.add_argument('--yahoo_email', type=str, required=True, help='Yahoo email address for account login.')
    parser.add_argument('--yahoo_pw', type=str, required=True, help='Password for Yahoo account login.')
    parser.add_argument('--yahoo_league_id', type=str, required=True, help='ID associated with Yahoo '
                                                                           'fantasy football league.')
    parser.add_argument('--yahoo_league_year', type=str, required=True, help='Current league year to extract '
                                                                             'player season projections from.')
    return parser.parse_args()


def yahoo_account_login(user_email, user_pw, browser):
    """
    Login to yahoo account to access fantasy football player projections based on league settings.
    """

    browser.get('https://login.yahoo.com')
    email_elem = browser.find_element_by_id('login-username')
    email_elem.send_keys(user_email)
    login_btn = browser.find_element_by_id('login-signin')
    login_btn.click()
    pw_elem = WebDriverWait(browser, 10).until(
        expected_conditions.presence_of_element_located((By.ID, 'login-passwd'))
    )
    pw_elem.send_keys(user_pw)
    submit_btn = browser.find_element_by_id('login-signin')
    submit_btn.click()
    return browser


def main():
    start, args = init_config()
    print('Program started\n**************START**************\n')

    # Create output file headers
    csv_extract = datetime.now().strftime('%Y_%m_%d_') + 'yahoo_player_season_projections.csv'
    with open(csv_extract, 'a') as output_file:
        output_file.write(
            'PLAYER_NAME,TEAM,POSITION,PLAYER_STATUS,GP*,BYE,FANTASY_POINTS,PRESEASON_RANKING,ACTUAL_RANKING,%_ROSTERED,PASSING_YDS,'
            'PASSING_TD,PASSING_INT,RUSHING_ATT,RUSHING_YDS,RUSHING_TD,RECEPTIONS,RECEIVING_YDS,RECEIVING_TD,TARGETS,RET_TD,'
            '2PT_CONVERSIONS,FUMBLES_LOST')

    # Remotely control safari web browser
    browser = webdriver.Safari()
    browser = yahoo_account_login(args.yahoo_email, args.yahoo_pw, browser)

    # Cycle through player data and extract season-long projections
    print('Extracting Yahoo! fantasy football player season projections...')
    pagination = 0  # Initialize at player 0
    while pagination <= 275:  # Last page begins at player 275, extract top 300 player projections by points
        browser.get('https://football.fantasysports.yahoo.com/f1/{0}/players?&sort=PTS&sdir=1&status=A&pos=O&stat1=S_PS_{1}&count={2}'
                    .format(args.yahoo_league_id, args.yahoo_league_year, str(pagination)))

        # Extract data from first web page table
        tables = browser.find_elements_by_class_name('Table')
        table_data = tables[0].get_attribute('innerText')
        table_rows = table_data.splitlines()
        del table_rows[:38]  # Remove header rows

        # Initialize variables
        i = 0
        player_details = []
        player_status = 'A'  # Player without a status has a null record, so default to 'A' (Active/Available)
        player_projections = []

        # Parse records and write to output file
        for table_row in table_rows:
            if i == 0:  # Capture player name, team, and position from first record
                player_details = table_row.split(' ')
                print(' '.join(player_details[:-3]))
                i += 1
            # Handle other player statuses
            elif table_row.lower() in ('ir', 'nfi-r', 'nfi-a', 'o', 'pup', 'pup-p', 'd', 'na', 'p', 'q', 'susp'):
                player_status = table_row
                continue
            elif i in (1, 2, 3, 23):  # Skip specific unused records using iterator
                i += 1
                pass
            elif 'note' in table_row.lower():  # Write current player projections and advance to next player
                i = 0
                csv_contents = '\n' + ' '.join(player_details[:-3]) \
                               + '{0}' + player_details[-3] + '{0}' + player_details[-1] + '{0}' + player_status + '{0}'
                for player_projection in player_projections:
                    csv_contents = csv_contents + player_projection + '{0}'
                with open(csv_extract, 'a') as output_file:
                    output_file.write(csv_contents.format(',')[:-1])
                # Reset variables
                player_projections = []
                player_status = 'A'
                continue
            else:  # Store player projection figures in list
                player_projections.append(table_row)
                i += 1
                continue

        pagination += 25  # Paginate to the next 25 players

    end = time.time()
    print('Program finished\n\n**************DONE**************\n' + 'Time elapsed: ' + str(end - start) + '\n')


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        raise err
