#!/usr/bin/python
__author__ = 'agoss'

import argparse
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def init_config():
    start = time.time()
    arg_list = get_arg_list()
    return start, arg_list


# listing the arguments that can be passed in though the command line
def get_arg_list():
    parser = argparse.ArgumentParser(description='Parses command line arguments')
    parser.add_argument('--yahoo_email', type=str, required=True, help='Yahoo email address for account login.')
    parser.add_argument('--yahoo_pw', type=str, required=True, help='Password for Yahoo account login.')
    parser.add_argument('--yahoo_league_id', type=str, required=True, help='ID associated with Yahoo '
                                                                           'fantasy football league.')
    return parser.parse_args()


def yahoo_account_login(user_email, user_pw, browser):
    """
    Login to yahoo account to access fantasy football league data.
    """

    browser.get('https://login.yahoo.com')
    email_elem = browser.find_element_by_id('login-username')
    email_elem.send_keys(user_email)
    login_btn = browser.find_element_by_id("login-signin")
    login_btn.click()
    pw_elem = WebDriverWait(browser, 10).until(
        expected_conditions.presence_of_element_located((By.ID, "login-passwd"))
    )
    pw_elem.send_keys(user_pw)
    submit_btn = browser.find_element_by_id("login-signin")
    submit_btn.click()
    return browser


def main():
    start, args = init_config()
    print('Program started\n**************START**************\n')

    # create output file headers
    with open("yahoo_average_auction_values.csv", "a") as output_file:
        output_file.write('PLAYER_NAME,TEAM,POSITION,LEAGUE_VALUE,PROJ_VALUE,AVG_COST,PREVIOUS_OWNER')

    # remotely control safari web browser
    browser = webdriver.Safari()
    browser = yahoo_account_login(args.yahoo_email, args.yahoo_pw, browser)

    #  cycle through player data and extract fantasy football league pre-draft auction values
    print('Extracting Yahoo! fantasy football player auction values...')
    pagination = 0  # initialize at player 0
    while pagination <= 250:  # last page begins at player 250, extract top 300 player auction values
        browser.get("https://football.fantasysports.yahoo.com/f1/" + args.yahoo_league_id + "/3/prerank_auction_costs"
                    "?filter=ALL&sort=TAC&count=" + str(pagination))

        # selenium hands off the source of the specific job page to beautiful soup for parsing
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        table = soup.find('table', id='ysf-preauctioncosts-dt')

        for row in table.select('tr'):
            if row.attrs['class'][0] == 'headerRow1':
                pass
            else:
                fantasy_data = row.text.splitlines()
                player_data = fantasy_data[3].split(' ')

                print(" ".join(player_data[:-4]))
                with open("yahoo_average_auction_values.csv", "a") as output_file:
                    output_file.write('\n' + " ".join(player_data[:-4]) + ',' + player_data[-4] + ','
                                      + player_data[-2] + ',' + fantasy_data[10] + ',' + fantasy_data[11] + ','
                                      + fantasy_data[12] + ',' + fantasy_data[13])
        pagination += 50  # paginate to the next 50 players

    end = time.time()
    print('Program finished\n\n**************DONE**************\n' + 'Time elapsed: ' + str(end - start) + '\n')


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        raise err
