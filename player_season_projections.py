#!/usr/bin/python3
__author__ = 'agoss'

import argparse
from datetime import datetime
import time

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
    parser.add_argument('--yahoo_league_id', type=str, required=True, help='ID associated with Yahoo '
                                                                           'fantasy football league.')
    parser.add_argument('--yahoo_league_year', type=str, required=True, help='Current league year to extract '
                                                                             'player season projections from.')
    return parser.parse_args()


def write_player_record_to_csv(csv_extract, player_details, player_status, player_projections):
    csv_contents = '\n' + player_details[0] + '{0}' + player_details[1] + '{0}' + player_details[2] + '{0}' + player_status + '{0}'
    for player_projection in player_projections:
        csv_contents = csv_contents + player_projection + '{0}'
    with open(csv_extract, 'a', encoding='utf-8') as output_file:
        output_file.write(csv_contents.format(',')[:-1])


def main():
    start, args = init_config()
    print('Program started\n**************START**************\n')

    # Create output file headers
    csv_extract = datetime.now().strftime('%Y_%m_%d_') + 'yahoo_player_season_projections.csv'
    with open(csv_extract, 'a', encoding='utf-8') as output_file:
        output_file.write(
            'PLAYER_NAME,TEAM,POSITION,PLAYER_STATUS,GP*,BYE,FANTASY_POINTS,PRESEASON_RANKING,ACTUAL_RANKING,PCT_ROSTERED,PASSING_YDS,'
            'PASSING_TD,PASSING_INT,RUSHING_ATT,RUSHING_YDS,RUSHING_TD,RECEPTIONS,RECEIVING_YDS,RECEIVING_TD,TARGETS,RET_TD,'
            '2PT_CONVERSIONS,FUMBLES_LOST')

    # Remotely control safari web browser
    browser = webdriver.Safari()
    browser = helper.yahoo_account_login(args.yahoo_email, args.yahoo_pw, browser)

    # Cycle through player data and extract season-long projections
    print('Extracting Yahoo! fantasy football player season projections...')
    pagination = 0  # Initialize at player 0
    while pagination <= 275:  # Last page begins at player 275, extract top 300 player projections by points
        time.sleep(5)  # Delay by 5 seconds
        browser.get(f'https://football.fantasysports.yahoo.com/f1/{args.yahoo_league_id}/players?&sort=PTS&sdir=1&status=A'
                    f'&pos=O&stat1=S_PS_{args.yahoo_league_year}&count={str(pagination)}')
        time.sleep(5)  # Delay by 5 seconds
        # Extract data from first web page table
        tables = browser.find_elements(By.CLASS_NAME, 'Table')
        table_data = tables[0].get_attribute('innerText')
        table_rows = table_data.splitlines()
        del table_rows[:37]  # Remove header rows
        del table_rows[0]  # Remove first row
        del table_rows[0]  # Remove second row

        # Initialize variables
        i = 0
        player_details = []
        player_status = 'A'  # Player without a status has a null record, so default to 'A' (Active/Available)
        player_projections = []
        ir_splits = ['IRVideo', 'IRNew', 'IRPlayer', 'IRNo new']
        nfi_r_splits = ['NFI-RVideo', 'NFI-RNew', 'NFI-RPlayer', 'NFI-RNo new']
        nfi_a_splits = ['NFI-AVideo', 'NFI-ANew', 'NFI-APlayer', 'NFI-ANo new']
        o_splits = ['OVideo', 'ONew', 'OPlayer', 'ONo new']
        pup_splits = ['PUPVideo', 'PUPNew', 'PUPPlayer', 'PUPNo new']
        pup_p_splits = ['PUP-PVideo', 'PUP-PNew', 'PUP-PPlayer', 'PUP-PNo new']
        d_splits = ['DVideo', 'DNew', 'DPlayer', 'DNo new']
        na_splits = ['NAVideo', 'NANew', 'NAPlayer', 'NANo new']
        p_splits = ['PVideo', 'PNew', 'PPlayer', 'PNo new']
        q_splits = ['QVideo', 'QNew', 'QPlayer', 'QNo new']
        susp_splits = ['SUSPVideo', 'SUSPNew', 'SUSPPlayer', 'SUSPNo new']

        # Parse records and write to output file
        for table_row in table_rows:
            if table_row.lower() in ('', ''):
                continue
            if i == 0:  # Capture player name from record
                # Handle player statuses
                if any(ir_split in table_row for ir_split in ir_splits):
                    player_status = 'IR'
                    for ir_split in ir_splits:
                        if ir_split in table_row:
                            player_details.append(table_row.split(ir_split, 1)[0])
                            break
                    i += 1
                    continue
                if any(nfi_r_split in table_row for nfi_r_split in nfi_r_splits):
                    player_status = 'NFI-R'
                    for nfi_r_split in nfi_r_splits:
                        if nfi_r_split in table_row:
                            player_details.append(table_row.split(nfi_r_split, 1)[0])
                            break
                    i += 1
                    continue
                if any(nfi_a_split in table_row for nfi_a_split in nfi_a_splits):
                    player_status = 'NFI-A'
                    for nfi_a_split in nfi_a_splits:
                        if nfi_a_split in table_row:
                            player_details.append(table_row.split(nfi_a_split, 1)[0])
                            break
                    i += 1
                    continue
                if any(o_split in table_row for o_split in o_splits):
                    player_status = 'O'
                    for o_split in o_splits:
                        if o_split in table_row:
                            player_details.append(table_row.split(o_split, 1)[0])
                            break
                    i += 1
                    continue
                if any(pup_split in table_row for pup_split in pup_splits):
                    player_status = 'PUP'
                    for pup_split in pup_splits:
                        if pup_split in table_row:
                            player_details.append(table_row.split(pup_split, 1)[0])
                            break
                    i += 1
                    continue
                if any(pup_p_split in table_row for pup_p_split in pup_p_splits):
                    player_status = 'PUP-P'
                    for pup_p_split in pup_p_splits:
                        if pup_p_split in table_row:
                            player_details.append(table_row.split(pup_p_split, 1)[0])
                            break
                    i += 1
                    continue
                if any(d_split in table_row for d_split in d_splits):
                    player_status = 'D'
                    for d_split in d_splits:
                        if d_split in table_row:
                            player_details.append(table_row.split(d_split, 1)[0])
                            break
                    i += 1
                    continue
                if any(na_split in table_row for na_split in na_splits):
                    player_status = 'NA'
                    for na_split in na_splits:
                        if na_split in table_row:
                            player_details.append(table_row.split(na_split, 1)[0])
                            break
                    i += 1
                    continue
                if any(p_split in table_row for p_split in p_splits):
                    player_status = 'P'
                    for p_split in p_splits:
                        if p_split in table_row:
                            player_details.append(table_row.split(p_split, 1)[0])
                            break
                    i += 1
                    continue
                if any(q_split in table_row for q_split in q_splits):
                    player_status = 'Q'
                    for q_split in q_splits:
                        if q_split in table_row:
                            player_details.append(table_row.split(q_split, 1)[0])
                            break
                    i += 1
                    continue
                if any(susp_split in table_row for susp_split in susp_splits):
                    player_status = 'SUSP'
                    for susp_split in susp_splits:
                        if susp_split in table_row:
                            player_details.append(table_row.split(susp_split, 1)[0])
                            break
                    i += 1
                    continue
                if 'Video Forecast' in table_row:
                    player_details.append(table_row.split('Video Forecast', 1)[0])
                elif 'New Player Note' in table_row:
                    player_details.append(table_row.split('New Player Note', 1)[0])
                elif 'Player Note' in table_row:
                    player_details.append(table_row.split('Player Note', 1)[0])
                elif 'No new player Notes' in table_row:
                    player_details.append(table_row.split('No new player Notes', 1)[0])
                i += 1
                continue
            if i == 1:  # Capture team and position from record
                team_pos = table_row.split(' ')
                player_details.append(team_pos[0])  # NFL team
                player_details.append(team_pos[2])  # Position
                print(f'{player_details[0]} - {player_details[2]} - {player_details[1]}')
                i += 1
                continue
            if i in (2, 3):  # Skip specific unused record using iterator
                i += 1
                continue
            if table_row.lower() == '':  # Write current player projections and advance to next player
                write_player_record_to_csv(csv_extract, player_details, player_status, player_projections)
                # Reset variables
                i = 0
                player_details = []
                player_status = 'A'
                player_projections = []
                continue
            # Store player projection figures in list
            player_projections.append(table_row)
            i += 1
            continue

        write_player_record_to_csv(csv_extract, player_details, player_status, player_projections)  # Write final page record
        pagination += 25  # Paginate to the next 25 players

    end = time.time()
    print('Program finished\n\n**************DONE**************\n' + 'Time elapsed: ' + str(end - start) + '\n')


if __name__ == '__main__':
    try:
        main()
    except RuntimeError as err:
        raise err
