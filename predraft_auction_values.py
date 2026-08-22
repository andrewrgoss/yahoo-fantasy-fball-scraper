#!/usr/bin/python3
__author__ = 'agoss'

import argparse
import csv
from datetime import datetime
import getpass
import os
from pathlib import Path
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
    parser.add_argument(
        '--yahoo-email', '--yahoo_email',
        dest='yahoo_email',
        type=str,
        default=os.getenv('YAHOO_EMAIL'),
        help='Yahoo email address. If omitted, the CLI prompts for it.',
    )
    parser.add_argument(
        '--yahoo-password', '--yahoo_pw',
        dest='yahoo_password',
        type=str,
        default=os.getenv('YAHOO_PASSWORD'),
        help='Yahoo password. Omit this option to receive a hidden password prompt.',
    )
    parser.add_argument(
        '--yahoo-league-id', '--yahoo_league_id',
        dest='yahoo_league_id',
        type=str,
        default=os.getenv('YAHOO_LEAGUE_ID'),
        help='ID associated with the Yahoo fantasy football league.',
    )
    parser.add_argument(
        '--manual-login',
        action='store_true',
        help='Open Yahoo in Safari and let the user complete login manually.',
    )
    parser.add_argument(
        '--output', '--output-file',
        dest='output_path',
        type=Path,
        help='Exact CSV output path. Defaults to a date-stamped file in the current directory.',
    )
    parser.add_argument(
        '--output-dir',
        dest='output_dir',
        type=Path,
        default=Path.cwd(),
        help='Directory for the default date-stamped CSV output.',
    )
    return parser.parse_args()


def manual_yahoo_login(browser):
    """Open Yahoo and pause while the user completes login in Safari."""

    browser.get('https://login.yahoo.com')
    input('Complete Yahoo login in Safari, then press Enter here to continue: ')
    return browser


def resolve_arguments(args):
    """Resolve interactive values without putting a password in shell history."""

    if not args.yahoo_league_id:
        raise ValueError('A Yahoo league ID is required (use --yahoo-league-id).')
    if args.manual_login:
        return args
    if not args.yahoo_email:
        args.yahoo_email = input('Yahoo email: ').strip()
    if not args.yahoo_password:
        args.yahoo_password = getpass.getpass('Yahoo password: ')
    if not args.yahoo_email or not args.yahoo_password:
        raise ValueError('Yahoo email and password are required unless --manual-login is used.')
    return args


def resolve_output_path(args):
    """Return the requested output path and create its parent directory."""

    if args.output_path:
        output_path = args.output_path
    else:
        output_path = args.output_dir / (
            datetime.now().strftime('%Y_%m_%d_') + 'yahoo_predraft_auction_values.csv'
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def main():
    start, args = init_config()
    args = resolve_arguments(args)
    print('Program started\n**************START**************\n')

    # Create output file headers
    csv_extract = resolve_output_path(args)
    with csv_extract.open('w', encoding='utf-8', newline='') as output_file:
        csv.writer(output_file).writerow(
            ['PLAYER_NAME', 'TEAM', 'POSITION', 'LEAGUE_VALUE', 'PROJ_VALUE', 'AVG_COST', 'PREVIOUS_OWNER']
        )

    # Remotely control Safari web browser
    browser = webdriver.Safari()
    try:
        if args.manual_login:
            browser = manual_yahoo_login(browser)
        else:
            browser = helper.yahoo_account_login(args.yahoo_email, args.yahoo_password, browser)

        # Cycle through player data and extract fantasy football league pre-draft auction values.
        print('Extracting Yahoo! fantasy football player auction values...')
        pagination = 0  # Initialize at player 0
        with csv_extract.open('a', encoding='utf-8', newline='') as output_file:
            writer = csv.writer(output_file)
            while pagination <= 250:  # Last page begins at player 250, extract top 300 player auction values
                time.sleep(5)  # Delay by 5 seconds
                browser.get(f'https://football.fantasysports.yahoo.com/f1/{args.yahoo_league_id}/3/prerank_auction_costs?'
                            f'filter=ALL&sort=TAC&count={str(pagination)}')

                # Selenium hands off the source of the specific job page to Beautiful Soup for parsing.
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                table = soup.find('table', id='ysf-preauctioncosts-dt')
                if table is None:
                    raise RuntimeError(
                        'Yahoo auction-value table was not found. Confirm that Safari is logged in '
                        'and that the league is available for the requested season.'
                    )

                for row in table.select('tr'):
                    if row.attrs.get('class', [''])[0] == 'headerRow1':
                        continue

                    fantasy_data = row.text.splitlines()
                    player_name = row.contents[2].contents[1].contents[1].contents[1].attrs['alt']
                    team_pos = fantasy_data[10].split(' ')

                    print(player_name)
                    writer.writerow([
                        player_name,
                        team_pos[0],
                        team_pos[2],
                        fantasy_data[18],
                        fantasy_data[19],
                        fantasy_data[20],
                        fantasy_data[21],
                    ])
                pagination += 50  # Paginate to the next 50 players
    finally:
        browser.quit()

    end = time.time()
    print(f'CSV written to: {csv_extract}')
    print('Program finished\n\n**************DONE**************\n' + 'Time elapsed: ' + str(end - start) + '\n')


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        raise err
