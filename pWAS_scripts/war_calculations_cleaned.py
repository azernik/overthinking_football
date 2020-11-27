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
import pandas as pd
import numpy as np
import random
import cProfile
import time
import getopt

def help(exit_code = 1):
    print("""-----------------------------------------------------------------
ARGUMENTS
    -w => <csv> weekly xFpts REQUIRED
    -t => <csv> season-long xfpts REQUIRED
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
        opts, args = getopt.getopt(sys.argv[1:], "w:t:o:")
    except getopt.GetoptError:
        print("Error: Incorrect usage of getopts flags!")
        help() 
    
    options_dict = dict(opts)

    ## Required arguments
    try:
        weekly_xfpts_csv = options_dict['-w']
        season_long_xfpts_csv = options_dict['-t']
        output_file = options_dict['-o']
    except KeyError:
        print("Error: One of your required arguments does not exist.")
        help()

    ## Optional Arguments
    #minute_requirement = options_dict.get('-m', 60)

    print("Acceptable Inputs Given")

    driver(weekly_xfpts_csv, season_long_xfpts_csv, output_file)


def driver(weekly_xfpts_csv, season_long_xfpts_csv, output_file):

    num_sample = 500000

    xfpts_df = pd.read_csv(season_long_xfpts_csv)
    weekly_xfpts_df = pd.read_csv(weekly_xfpts_csv)

    fwd_group_dict = {1: [40, 35, 55],
                      2: [50, 40, 60],
                      3: [40, 35, 55]}

    mid_group_dict = {1: [50, 45, 65],
                      2: [60, 50, 80],
                      3: [55, 45, 70]}

    def_group_dict = {1: [40, 35, 55],
                      2: [50, 40, 60],
                      3: [50, 40, 60]}

    player_pwas_dict = {}
    player_dict = {}
    for group in list(fwd_group_dict.keys()):

        ## FWDS
        fwd_total_starters, fwd_ww_start, fwd_ww_end = fwd_group_dict[group]
        fwd_starter_game_scores, fwd_ww_game_scores = get_starters_and_ww("F", xfpts_df, weekly_xfpts_df, fwd_total_starters, fwd_ww_start, fwd_ww_end)
        
        ## MIDS
        mid_total_starters, mid_ww_start, mid_ww_end = mid_group_dict[group]
        mid_starter_game_scores, mid_ww_game_scores = get_starters_and_ww("M", xfpts_df, weekly_xfpts_df, mid_total_starters, mid_ww_start, mid_ww_end)
        
        ## DEF
        def_total_starters, def_ww_start, def_ww_end = def_group_dict[group]
        def_starter_game_scores, def_ww_game_scores = get_starters_and_ww("F", xfpts_df, weekly_xfpts_df, def_total_starters, def_ww_start, def_ww_end)
        
        starter_score_dict = {"D": def_starter_game_scores,
                              "M": mid_starter_game_scores,
                              "F": fwd_starter_game_scores}
        ww_score_dict = {"D": def_ww_game_scores,
                         "M": mid_ww_game_scores,
                         "F": fwd_ww_game_scores}
        ### Average Starter team sampling

        starter_avg_game = []
        ww_def_avg_game = []
        ww_mid_avg_game = []
        ww_fwd_avg_game = []
        start = time.time()
    
        formation_list = [[3,4,3], [3,5,2], [4,4,2], [4,3,3]]

        for formation in formation_list:

            def_formation_count, mid_formation_count, fwd_formation_count = formation

            ## first get the average game with all starters
            starter_lineup_avg_game = get_game_results(starter_score_dict, formation, num_sample)
            starter_avg_game = starter_avg_game + starter_lineup_avg_game

            ## Average games for one player missing at each position
            # DEF
            def_missing_formation = formation[:]
            def_missing_formation[0] -= 1
            ww_def_included_avg_game = get_game_results(starter_score_dict, def_missing_formation, num_sample, ww_score_dict['D'])
            ww_def_avg_game = ww_def_avg_game + ww_def_included_avg_game

            # MID
            mid_missing_formation = formation[:]
            mid_missing_formation[1] -= 1 #NOTE should be 1 instead of 0?
            ww_mid_included_avg_game = get_game_results(starter_score_dict, mid_missing_formation, num_sample, ww_score_dict['M'])
            ww_mid_avg_game = ww_mid_avg_game + ww_mid_included_avg_game

            # FWD
            fwd_missing_formation = formation[:]
            fwd_missing_formation[2] -= 1 #NOTE should be 2 instead of 0?
            ww_fwd_included_avg_game = get_game_results(starter_score_dict, fwd_missing_formation, num_sample, ww_score_dict['F'])
            ww_fwd_avg_game = ww_fwd_avg_game + ww_fwd_included_avg_game

        # shuffle the avg game data and calculate the ww_pwas values
        random.shuffle(starter_avg_game)

        def_ww_win_percentage = get_win_percentage(ww_def_avg_game, starter_avg_game)
        def_ww_war = def_ww_win_percentage - 0.5
        print('Mean def ww game score: ', np.mean(ww_def_avg_game))
        print('std def ww game score: ', np.std(ww_def_avg_game))
        print("DEF avg war lost: ", def_ww_war)

        mid_ww_win_percentage = get_win_percentage(ww_mid_avg_game, starter_avg_game)
        mid_ww_war = mid_ww_win_percentage - 0.5
        print('Mean mid ww game score: ', np.mean(ww_mid_avg_game))
        print('std mid ww game score: ', np.std(ww_mid_avg_game))
        print("MID avg war lost: ", mid_ww_war)

        fwd_ww_win_percentage = get_win_percentage(ww_fwd_avg_game, starter_avg_game)
        fwd_ww_war = fwd_ww_win_percentage - 0.5
        print('Mean fwd ww game score: ', np.mean(ww_fwd_avg_game))
        print('std fwd ww game score: ', np.std(ww_fwd_avg_game))
        print("FWD avg war lost: ", fwd_ww_war)

        ## Next cycle through each player
        ## For all players SAMPLING procedure
        #player_dict = {}
        for index, row in xfpts_df.iterrows():
            print(index)
            
            sim_games = []
            player = row['Player']
            pos = row['Position']
            games = row['n']
            #print(player)
            player_weekly_pts = weekly_xfpts_df.loc[(weekly_xfpts_df['Player'] == player)]['xFpts']
            if player_weekly_pts.empty:
                print(player + " is missing from weekly pts")
                continue
            
            for formation in formation_list:
                def_formation_count, mid_formation_count, fwd_formation_count = formation
                def_count = def_formation_count
                mid_count = mid_formation_count
                fwd_count = fwd_formation_count
                if pos == 'D':
                    def_count -= 1
                    ww_pwas = def_ww_war
                elif pos == 'M':
                    mid_count -= 1
                    ww_pwas = mid_ww_war
                elif pos == 'F':
                    fwd_count -= 1
                    ww_pwas = fwd_ww_war
                
                def_index_pos = 0
                mid_index_pos = 0
                fwd_index_pos = 0

                player_samples = list(player_weekly_pts.sample(n = num_sample, replace = True))
                def_samples = list(def_starter_game_scores.sample(n=(def_count * num_sample), replace = True))
                mid_samples = list(mid_starter_game_scores.sample(n=(mid_count * num_sample), replace = True))
                fwd_samples = list(fwd_starter_game_scores.sample(n=(fwd_count * num_sample), replace = True))
                 
                for sample in range(num_sample):
                    def_index_2 = def_index_pos + def_count
                    mid_index_2 = mid_index_pos + mid_count
                    fwd_index_2 = fwd_index_pos + fwd_count
                    total_pts = 0
                    def_pts = def_samples[def_index_pos:def_index_2]
                    mid_pts = mid_samples[mid_index_pos:mid_index_2]
                    fwd_pts = fwd_samples[fwd_index_pos:fwd_index_2]
                    player_sample = player_samples[sample]

                    all_pts = def_pts + mid_pts + fwd_pts + [player_sample]
                    for pts in all_pts:
                        total_pts += pts

                    def_index_pos = def_index_2
                    mid_index_pos = mid_index_2
                    fwd_index_pos = fwd_index_2

                    sim_games.append(total_pts)

            sim_games_mean = np.mean(sim_games)
            sim_games_sd = np.std(sim_games)
            
            win_percentage = get_win_percentage(sim_games, starter_avg_game)
            pwas = win_percentage - 0.5
            games_missed = 38 - games
            try:
                print(row)
                player_dict[player][3] += pwas
                player_dict[player][4] += ww_pwas
                #print(pwas)
                #print(ww_pwas)

            except KeyError:
                player_dict[player] = [pos, games, games_missed, pwas, ww_pwas]
               # print(player_dict[player])

    ## Finally clean up player dict
    final_player_dict = {}
    for player in player_dict:
        total_groups = len(list(fwd_group_dict.keys()))
        #print(total_groups)
        pos, games, games_missed, pwas, ww_pwas = player_dict[player]
        print(player_dict[player])
        avg_pwas = pwas / float(total_groups)
        print(avg_pwas)
        avg_ww_pwas = ww_pwas / float(total_groups)
        print(avg_ww_pwas)
        pwar = avg_pwas - avg_ww_pwas
        final_player_dict[player] = [pos, \
                                     games, \
                                     games_missed, \
                                     avg_pwas, \
                                     avg_ww_pwas, \
                                     pwar,
                                     pwar * float(games)]

    ## convert player dict to pandas df
    df = pd.DataFrame.from_dict(final_player_dict, orient='index', columns = ['Pos', 'games_played', 'games_missed', 'pWAS', 'ww_pWAS', 'pWAR', 'WAR'])

    df = df.sort_values(by = 'WAR', ascending = False)

    df.to_csv(output_file)



def get_game_results(starter_score_dict, pos_counts, num_sample, ww_added_df = None):

    def_count, mid_count, fwd_count = pos_counts

    def_samples = list(starter_score_dict['D'].sample(n=def_count*num_sample, replace = True))
    mid_samples = list(starter_score_dict['M'].sample(n=mid_count*num_sample, replace = True))
    fwd_samples = list(starter_score_dict['F'].sample(n=fwd_count*num_sample, replace = True))
    if ww_added_df is not None:
        ww_samples = list(ww_added_df.sample(n=num_sample, replace = True))

    def_index_pos = 0
    mid_index_pos = 0
    fwd_index_pos = 0

    game_list = []

    for sample in range(num_sample):
        def_index_2 = def_index_pos + def_count
        mid_index_2 = mid_index_pos + mid_count
        fwd_index_2 = fwd_index_pos + fwd_count
        total_pts = 0
        def_pts = def_samples[def_index_pos:def_index_2]
        mid_pts = mid_samples[mid_index_pos:mid_index_2]
        fwd_pts = fwd_samples[fwd_index_pos:fwd_index_2]
        all_pts = def_pts + mid_pts + fwd_pts
        for pts in all_pts:
            total_pts += pts
        if ww_added_df is not None:
            ww_pts = ww_samples[sample]
            total_pts += ww_pts


        def_index_pos = def_index_2
        mid_index_pos = mid_index_2
        fwd_index_pos = fwd_index_2

        game_list.append(total_pts)
    
    return game_list   



def get_starters_and_ww(pos, xfpts_df, weekly_xfpts_df, total_starters, ww_start, ww_end):

    starters = list(xfpts_df.loc[(xfpts_df['Position'] == pos) & (xfpts_df['n'] >= 10)].sort_values(by = 'mean_xFpts', ascending = False)[0:total_starters]['Player'])
    print(pos + " starters: \n", starters)
    starter_game_scores = weekly_xfpts_df.loc[(weekly_xfpts_df['Player'].isin(starters))]['xFpts']
    ww_players = list(xfpts_df.loc[(xfpts_df['Position'] == pos) & (xfpts_df['n'] >= 5)].sort_values(by = 'mean_xFpts', ascending = False)[ww_start:ww_end]['Player'])
    print(pos + " ww: \n", ww_players)
    ww_game_scores = weekly_xfpts_df.loc[(weekly_xfpts_df['Player'].isin(ww_players))]['xFpts']

    return starter_game_scores, ww_game_scores


def get_win_percentage(game_list_1, game_list_2):
    
    num_matchups = len(game_list_1)

    diff = np.array(game_list_1) - np.array(game_list_2)
    
    win_count = 0
    for d in diff:
        if d > 0:
            win_count += 1
    win_percentage = win_count / num_matchups

    return win_percentage


if __name__ == "__main__":
    main(sys.argv[1:])
 
