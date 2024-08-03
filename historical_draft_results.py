#!/usr/bin/python3
__author__ = 'agoss'

import argparse
from io import StringIO
import re
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

import helper


def init_config():
    start = time.time()
    arg_list = get_arg_list()
    return start, arg_list


# Listing the arguments that can be passed in though the command line
def get_arg_list():
    parser = argparse.ArgumentParser(description='Parses command line arguments')
    parser.add_argument('--yahoo_email', type=str, required=True, help='Yahoo email address for account login.')
    parser.add_argument('--yahoo_pw', type=str, required=True, help='Password for Yahoo account login.')
    parser.add_argument('--yahoo_league_name', type=str, required=True, help='Name associated with Yahoo fantasy football league.')
    parser.add_argument('--yahoo_league_year', type=str, required=True, help='Historical league year to extract auction draft results.')
    return parser.parse_args()


def main():
    start, args = init_config()
    print('Program started\n**************START**************\n')

    # Remotely control Safari web browser
    browser = webdriver.Safari()
    browser = helper.yahoo_account_login(args.yahoo_email, args.yahoo_pw, browser)

    # Obtain historical fantasy football league details using yahoo player profile
    time.sleep(5)  # Delay by 5 seconds
    browser.get('https://profiles.sports.yahoo.com/?sport=football')

    # Search web page elements to find and click button for user fantasy football league history
    elements = browser.find_elements(By.XPATH, '//*[contains(text(), \'History\')]')
    for element in elements:
        if element.get_attribute('textContent') == 'History':
            element.click()

    # For supplied league year, extract auction draft results
    elements = browser.find_elements(By.XPATH, f'//a[contains(@href, \'https://football.fantasysports.yahoo.com/{args.yahoo_league_year}/\')]')

    for element in elements:
        # Locate auction draft results and sort by descending player acquisition cost
        if args.yahoo_league_name in element.get_attribute('outerText'):
            browser.get(element.get_attribute('href') + '/draftresults?drafttab=picks&sort=cost&order_by=desc')
            tables = browser.find_elements(By.CLASS_NAME, 'Table')

            for table in tables:
                table_data = table.get_attribute('innerText')
                # Use page table header that has draft pick data and transform within Pandas dataframe
                if table_data[0:4] == 'Pick':
                    df = pd.read_csv(StringIO(table_data), delimiter='\t', lineterminator='\n')
                    df['Pick'] = df['Pick'].astype(int)
                    df.insert(0, 'Year', args.yahoo_league_year)
                    df.rename(columns={'Team': 'Owner'}, inplace=True)
                    df['Player'] = df['Player'].str.replace(' \\ue03e', '', regex=True)

                    # Split out player data into additional dataframe columns
                    df.insert(3, 'Team',
                              [re.search(r'\(([^\)]+)\)', str(x)).group(1).split(' ')[0] for x in df['Player']])
                    df.insert(4, 'Position',
                              [re.search(r'\(([^\)]+)\)', str(x)).group(1).split(' ')[2] for x in df['Player']])
                    df['Player'] = [re.sub(r'[(].*?[)]', '', str(x)).rstrip() for x in df['Player']]

                    # Write formatted data for supplied historical league year(s) to csv file
                    print(f'Writing to file...yahoo_{args.yahoo_league_name}_{args.yahoo_league_year}_draft_results.csv')
                    df.to_csv(f'yahoo_{args.yahoo_league_name}_{args.yahoo_league_year}_draft_results.csv', index=False)

    end = time.time()
    print('Program finished\n\n**************DONE**************\n' + 'Time elapsed: ' + str(end - start) + '\n')


if __name__ == '__main__':
    try:
        main()
    except RuntimeError as err:
        raise err
