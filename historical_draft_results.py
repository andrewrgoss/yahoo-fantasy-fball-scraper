#!/usr/bin/python3
__author__ = 'agoss'

import argparse
from io import StringIO
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import time


def init_config():
    start = time.time()
    arg_list = get_arg_list()
    return start, arg_list


# listing the arguments that can be passed in though the command line
def get_arg_list():
    parser = argparse.ArgumentParser(description='Parses command line arguments')
    parser.add_argument('--yahoo_email', type=str, required=True, help='Yahoo email address for account login.')
    parser.add_argument('--yahoo_pw', type=str, required=True, help='Password for Yahoo account login.')
    parser.add_argument('--yahoo_league_name', type=str, required=True, help='Name associated with Yahoo '
                                                                             'fantasy football league.')
    parser.add_argument('--yahoo_league_year', type=str, required=True, help='Historical league year to extract '
                                                                             'auction draft results from.')
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

    # remotely control safari web browser
    browser = webdriver.Safari()
    browser = yahoo_account_login(args.yahoo_email, args.yahoo_pw, browser)

    # obtain historical fantasy football league details using yahoo player profile
    browser.get("https://profiles.sports.yahoo.com/?sport=football")

    # search web page elements to find and click button for user fantasy football league history
    elements = browser.find_elements_by_xpath("//*[contains(text(), 'History')]")
    for element in elements:
        if element.get_attribute('textContent') == 'History':
            element.click()

    # for supplied league year, extract auction draft results
    elements = browser.find_elements_by_xpath(
        '//a[contains(@href, "https://football.fantasysports.yahoo.com/{0}/")]'.format(args.yahoo_league_year))

    for element in elements:
        # locate auction draft results and sort by descending player acquisition cost
        if args.yahoo_league_name in element.get_attribute('outerText'):
            browser.get(element.get_attribute('href') + '/draftresults?drafttab=picks&sort=cost&order_by=desc')
            tables = browser.find_elements_by_class_name("Table")

            for table in tables:
                table_data = table.get_attribute('innerText')
                # use page table header that has draft pick data and transform within dataframe
                if table_data[0:4] == 'Pick':
                    df = pd.read_csv(StringIO(table_data), delimiter='\t', lineterminator='\n')
                    df['Pick'] = df['Pick'].astype(int)
                    df.insert(0, 'Year', args.yahoo_league_year)
                    df.rename(columns={'Team': 'Owner'}, inplace=True)
                    df['Player'] = df['Player'].str.replace(' \\ue03e', '', regex=True)

                    # split out player data into additional dataframe columns
                    df.insert(3, 'Team',
                              [re.search(r'\(([^\)]+)\)', str(x)).group(1).split(' ')[0] for x in df['Player']])
                    df.insert(4, 'Position',
                              [re.search(r'\(([^\)]+)\)', str(x)).group(1).split(' ')[2] for x in df['Player']])
                    df['Player'] = [re.sub(r'[(].*?[)]', '', str(x)).rstrip() for x in df['Player']]

                    # write formatted data for supplied historical league year(s) to csv file
                    print('Writing to file...yahoo_{0}_{1}_draft_results.csv'.format(args.yahoo_league_name,
                                                                                     args.yahoo_league_year))
                    df.to_csv('yahoo_{0}_{1}_draft_results.csv'.format(args.yahoo_league_name,
                                                                       args.yahoo_league_year), index=False)

    end = time.time()
    print('Program finished\n\n**************DONE**************\n' + 'Time elapsed: ' + str(end - start) + '\n')


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        raise err
