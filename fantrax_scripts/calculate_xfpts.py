#!/usr/bin/Python

# Created by: Christopher J Adams 9/29/2018
# 

###############################################################################
###
### This script calculates xfpts given the weekly game results
###
###############################################################################

#import cProfile
import sys
import getopt
import os
import re
import pandas as pd
import numpy as np
import yaml

def help(exit_code = 1):
    print("""-----------------------------------------------------------------
ARGUMENTS
    -r => <yaml> config file specifying the scoring rules REQUIRED
    -w => <csv> weekly game results downloaded from fantrax REQUIRED
    -x => <csv> expected statistics from fbref REQUIRED
    -c => <csv> match total xG data from fbref REQUIRED
    -m => <int> minute requirement OPTIONAL Default = 60
    -o => <path> name of output file REQUIRED
""")
    sys.exit(exit_code)
###############################################################################
###########################  COLLECT AND CHECK ARGUMENTS  #####################
###############################################################################


## MAIN ##

def main(argv): 
    pd.set_option('display.max_colwidth', 100)
    try: 
        opts, args = getopt.getopt(sys.argv[1:], "r:w:x:o:c:")
    except getopt.GetoptError:
        print("Error: Incorrect usage of getopts flags!")
        help() 
    
    options_dict = dict(opts)

    ## Required arguments
    try:
        rules_config_file = options_dict['-r']
        weekly_results_file = options_dict['-w']
        fbref_expected_table_file = options_dict['-x']
        cs_data_file = options_dict['-c']
        output_file = options_dict['-o']
    except KeyError:
        print("Error: One of your required arguments does not exist.")
        help()

    ## Optional Arguments
    minute_requirement = options_dict.get('-m', 60)

    print("Acceptable Inputs Given")

    driver(rules_config_file, weekly_results_file, fbref_expected_table_file, cs_data_file, minute_requirement, output_file)

 

###############################################################################
#############################  DRIVER  ########################################
###############################################################################


## drive the script ##
## ONE-TIME CALL -- called by main

def driver(rules_config_file, weekly_results_file, fbref_expected_table_file, cs_data_file, minute_requirement, output_file):

    rules_dict = yaml.load(open(rules_config_file, 'r'), Loader=yaml.SafeLoader)

    weekly_results_df = pd.read_csv(weekly_results_file)
    print("weekly fantrax data size: ", weekly_results_df.shape)
    fbref_weekly_df = pd.read_csv(fbref_expected_table_file)
    print("weekly fbref data size: ", fbref_weekly_df.shape)
    
    cs_df = get_relevant_cs_df(cs_data_file)
    print("clean sheet xg match data size: ", cs_df.shape)
    print(cs_df.tail())

    #print(cs_df)
    #sys.exit()
    ## trim to the minute limit
    weekly_results_df = weekly_results_df.loc[(weekly_results_df['Min'] >= minute_requirement) & (weekly_results_df['SubOn'] == 0) & (weekly_results_df['GP'] == 1)]
    print("fantrax weekly results size post filter: ", weekly_results_df.shape)
    ## get grouped summary df
    season_results_df = weekly_results_df.groupby(['Player', 'Team', 'Position']).size().reset_index(name='valid_starts')
    print("fantrax weekly results grouped size: ", season_results_df.shape)
    #sys.exit()
    #print(season_results_df)

    ## next merge the fantrax weekly data with the weekly fbref data
    #fix the date format of the fantrax weekly data
    dates = convert_dates(list(fbref_weekly_df['Date']))
    fbref_weekly_df['Date'] = dates

    fbref_data_merged_df = pd.merge(fbref_weekly_df, cs_df, on=['Team', 'Date'])
    print("weekly fbref data merged with cs data size: ",fbref_data_merged_df.shape)
    print(fbref_weekly_df.tail())
    #sys.exit()

    final_df = pd.merge(weekly_results_df, fbref_data_merged_df, on = ['Player', 'game_week'])
    print("Size of the final df: ",final_df.shape)

    calculate_xfpts(final_df, rules_dict)
    final_df.to_csv('~/Desktop/weekly_xfpts.20_21.csv')
    # get grouped df
    season_xfpts_df = group_final_df(final_df)
    #print(season_xfpts_df)

    season_xfpts_df.to_csv('~/Desktop/season_xfpts.20_21.csv')


def group_final_df(final_df):

    all_players = set(final_df['Player'])
    results_dict = {}

    player_list_header = ['Team', 'Position', 'Valid_starts', 'total_min', 'mean_min', 'mean_xFpts', 'sd_xFpts', 'mean_fpts', 'sd_fpts', 'mean_xFpts - mean_fpts', 'total_xFpts', 'total_fpts', 'total_xFpts - total_fpts', 'total_xCS', 'CS']

    for player in all_players:
        player_data_list = []
        player_df = final_df.loc[final_df['Player'] == player]

        team = list(player_df['Team_x'])[0]
        pos = list(player_df['Position'])[0]
        valid_starts = len(player_df)
        total_min = np.sum(player_df['Min_x'])
        mean_min = np.mean(player_df['Min_x'])
        mean_xFpts = np.mean(player_df['xFpts'])
        sd_xFpts = np.std(player_df['xFpts'])
        mean_fpts = np.mean(player_df['updated_fpts'])
        sd_fpts = np.std(player_df['updated_fpts'])

        total_xFpts = np.sum(player_df['xFpts'])
        total_fpts = np.sum(player_df['updated_fpts'])

        total_xCS = np.sum(player_df['xCS'])
        total_CS = np.sum(player_df['CS'])
        mean_diff = mean_xFpts - mean_fpts
        total_diff = total_xFpts - total_fpts
        player_data_list = [team, pos, valid_starts, total_min, mean_min, mean_xFpts, sd_xFpts, mean_fpts, sd_fpts, mean_diff, total_xFpts, total_fpts, total_diff, total_xCS, total_CS]

        results_dict[player] = player_data_list

    #print(results_dict)
    season_xfpts_df = pd.DataFrame.from_dict(data = results_dict, orient = 'index', columns = player_list_header)
    return season_xfpts_df

def calculate_xfpts(final_df, rules_dict):

    ## first adjust for xGA
    final_df['xGA'] = np.where(final_df['xG_against'] - 0.25 < 0, 0, final_df['xG_against'] - 0.25)
    final_df['xCS'] = np.where(final_df['xGA'] <= 1.25, 1 - final_df['xGA']/1.25, 0)
    xfpts_list = []
    standard_points_list = []
    for ind, row in final_df.iterrows():
        xfpts = 0
        standard_points = 0
        pos = row['Position']
        scoring_rules_dict = rules_dict[pos]
        for scoring_category in scoring_rules_dict:
            point_value = float(scoring_rules_dict[scoring_category])
            raw_points = point_value * float(row[scoring_category])

            standard_points += raw_points
            ## expected scaled categories
            if scoring_category in ['G', 'AT', 'A', 'CS', 'GAD']:
                scaled_points = 0
                if scoring_category == 'G':
                    scaled_points = point_value * float(row['xG'])
                elif scoring_category == 'AT':
                    scaled_points = float(row['xA']) * point_value + (float(row['AT']) - float(row['Ast'])) * point_value
                    #scaled_points = point_value * float(row['xA'])
                elif scoring_category == 'CS':
                    scaled_points = point_value * float(row['xCS'])
                elif scoring_category == 'GAD':
                    scaled_points = point_value * float(row['xGA'])
                xfpts += scaled_points
            else:
                xfpts += raw_points

        xfpts_list.append(xfpts)
        standard_points_list.append(standard_points)

    final_df['updated_fpts'] = standard_points_list
    final_df['xFpts'] = xfpts_list


    return final_df




def get_relevant_cs_df(cs_data_file):

    df = pd.read_csv(cs_data_file)
    #print(set(df['Date']))
    dates = convert_dates(list(df['Date']))
    #dates = list(df['Date'])
    cs_dict = {'Team': list(df['Home']) + list(df['Away']),
                'xG_against': list(df['xG.1']) + list(df['xG']),
                'game_week': list(df['Wk']) + list(df['Wk']),
                'h_a': (['h']*len(list(df['Home']))) + (['a']*len(list(df['Home']))),
                'Date': dates * 2}
    cs_df = pd.DataFrame(cs_dict)
    
    return cs_df


def convert_dates(dates):
    converted_dates = []
    for date in dates:
        date_list = date.split('/')
        new_date_string = ''
        count = 0
        for date_item in date_list:
            count += 1
            if len(date_item) == 1:
                convert_date_item = str(0) + str(date_item)
                new_date_string = new_date_string + convert_date_item + '/'
            elif len(date_item) == 2 and count != 3:
                new_date_string = new_date_string + date_item + '/'
            else:
                new_date_string = new_date_string + date_item
                converted_dates.append(new_date_string)

    return converted_dates

if __name__ == "__main__":
    main(sys.argv[1:])
