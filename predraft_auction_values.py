#!/usr/bin/python3
__author__ = 'agoss'

import argparse
from datetime import datetime
import time

from bs4 import BeautifulSoup
from selenium import webdriver

import helper


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


def main():
    start, args = init_config()
    print('Program started\n**************START**************\n')

    # Create output file headers
    csv_extract = datetime.now().strftime('%Y_%m_%d_') + 'yahoo_predraft_auction_values.csv'
    with open(csv_extract, 'a', encoding='utf-8') as output_file:
        output_file.write('PLAYER_NAME,TEAM,POSITION,LEAGUE_VALUE,PROJ_VALUE,AVG_COST,PREVIOUS_OWNER')

    # Remotely control Safari web browser
    browser = webdriver.Safari()
    browser = helper.yahoo_account_login(args.yahoo_email, args.yahoo_pw, browser)

    #  Cycle through player data and extract fantasy football league pre-draft auction values
    print('Extracting Yahoo! fantasy football player auction values...')
    pagination = 0  # Initialize at player 0
    while pagination <= 250:  # Last page begins at player 250, extract top 300 player auction values
        time.sleep(5)  # Delay by 5 seconds
        browser.get(f'https://football.fantasysports.yahoo.com/f1/{args.yahoo_league_id}/3/prerank_auction_costs?'
                    f'filter=ALL&sort=TAC&count={str(pagination)}')

        # Selenium hands off the source of the specific job page to Beautiful Soup for parsing
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        table = soup.find('table', id='ysf-preauctioncosts-dt')

        for row in table.select('tr'):
            if row.attrs['class'][0] == 'headerRow1':
                pass
            else:

                fantasy_data = row.text.splitlines()
                player_name = row.contents[2].contents[1].contents[1].contents[1].contents[0].text
                team_pos = row.contents[2].contents[1].contents[1].contents[1].contents[1].text
                team_pos = team_pos.split(' ')

                print(player_name)
                with open(csv_extract, 'a', encoding='utf-8') as output_file:
                    output_file.write(f'\n{player_name},{team_pos[0]},{team_pos[2]},'
                                      f'{fantasy_data[10]},{fantasy_data[11]},{fantasy_data[12]},{fantasy_data[13]}')
        pagination += 50  # Paginate to the next 50 players

    end = time.time()
    print('Program finished\n\n**************DONE**************\n' + 'Time elapsed: ' + str(end - start) + '\n')


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        raise err
