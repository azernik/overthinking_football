#!/usr/bin/Python

import sys
import pandas as pd
import numpy as np
import random
import cProfile
import time

def main(argv):
    
    fwd_num = 40
    mid_num = 50
    def_num = 40
    ## open data file
    xfpts_csv = "~/Documents/GitHub/overthinking_football/data/fantrax_data/no_min_requirement.updated_positions.xFpts_epl_2019_2020.csv"
    xfpts_df = pd.read_csv(xfpts_csv)

    weekly_xfpts_csv = "~/Documents/GitHub/overthinking_football/data/fantrax_data/weekly_data.no_min_requirement.updated_positions.xFpts_epl_2019_2020.csv"
    weekly_xfpts_df = pd.read_csv(weekly_xfpts_csv)

    num_sample = 500000

    ## get avg team 3-4-3 10 team league
    # SAMPLING METHOD no distribution
    # gather data to sample from
    
    ## FWDS
    
    fwd_starters = list(xfpts_df.loc[(xfpts_df['Position'] == 'F') & (xfpts_df['n'] >= 10)].sort_values(by = 'mean_xFpts', ascending = False)[0:fwd_num]['Player'])
    print("Forward starters: \n", fwd_starters)
    fwd_starter_game_scores = weekly_xfpts_df.loc[(weekly_xfpts_df['Player'].isin(fwd_starters))]['xFpts']
    fwd_ww = list(xfpts_df.loc[(xfpts_df['Position'] == 'F') & (xfpts_df['n'] >= 5)].sort_values(by = 'mean_xFpts', ascending = False)[35:55]['Player'])
    print("Forward ww: \n", fwd_ww)
    fwd_ww_game_scores = weekly_xfpts_df.loc[(weekly_xfpts_df['Player'].isin(fwd_ww))]['xFpts']
    
    ## MIDS
    mid_starters = list(xfpts_df.loc[(xfpts_df['Position'] == 'M') & (xfpts_df['n'] >= 10)].sort_values(by = 'mean_xFpts', ascending = False)[0:mid_num]['Player'])
    print("Mid starters: \n", mid_starters)
    mid_starter_game_scores = weekly_xfpts_df.loc[(weekly_xfpts_df['Player'].isin(mid_starters))]['xFpts']
    mid_ww = list(xfpts_df.loc[(xfpts_df['Position'] == 'M') & (xfpts_df['n'] >= 5)].sort_values(by = 'mean_xFpts', ascending = False)[45:65]['Player'])
    print("Mid ww: \n", mid_ww)
    mid_ww_game_scores = weekly_xfpts_df.loc[(weekly_xfpts_df['Player'].isin(mid_ww))]['xFpts']
    
    ## DEF
    def_starters = list(xfpts_df.loc[(xfpts_df['Position'] == 'D') & (xfpts_df['n'] >= 10)].sort_values(by = 'mean_xFpts', ascending = False)[0:def_num]['Player'])
    print("Def starters: \n",def_starters)
    def_starter_game_scores = weekly_xfpts_df.loc[(weekly_xfpts_df['Player'].isin(def_starters))]['xFpts']
    def_ww = list(xfpts_df.loc[(xfpts_df['Position'] == 'D') & (xfpts_df['n'] >= 5)].sort_values(by = 'mean_xFpts', ascending = False)[35:55]['Player'])
    print("Def ww: \n",def_ww)
    def_ww_game_scores = weekly_xfpts_df.loc[(weekly_xfpts_df['Player'].isin(def_ww))]['xFpts']
    
    ### Average Starter team sampling

    avg_game = []
    def_avg_game = []
    mid_avg_game = []
    fwd_avg_game = []
    start = time.time()
    
    formation_list = [[3,4,3], [3,5,2], [4,4,2], [4,3,3]]

    for formation in formation_list:
        print("formation: ", formation)
        def_formation_count, mid_formation_count, fwd_formation_count = formation
        formation_avg_game = []
        def_count = def_formation_count
        mid_count = mid_formation_count
        fwd_count = fwd_formation_count

        def_samples = list(def_starter_game_scores.sample(n=def_count*num_sample, replace = True))
        mid_samples = list(mid_starter_game_scores.sample(n=mid_count*num_sample, replace = True))
        fwd_samples = list(fwd_starter_game_scores.sample(n=fwd_count*num_sample, replace = True))
    
        def_index_pos = 0
        mid_index_pos = 0
        fwd_index_pos = 0
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

            def_index_pos = def_index_2
            mid_index_pos = mid_index_2
            fwd_index_pos = fwd_index_2

            formation_avg_game.append(total_pts)
        print(np.mean(formation_avg_game))
        print(np.std(formation_avg_game))
        avg_game = avg_game + formation_avg_game
        
        ### Average WW sampling for 1 player missing
        def_formation_avg_game = []
        mid_formation_avg_game = []
        fwd_formation_avg_game = []
        ## DEF
        def_count = def_formation_count - 1
        mid_count = mid_formation_count
        fwd_count = fwd_formation_count
        
        def_ww_samples = list(def_ww_game_scores.sample(n=num_sample, replace = True))
        def_samples = list(def_starter_game_scores.sample(n=def_count*num_sample, replace = True))
        mid_samples = list(mid_starter_game_scores.sample(n=mid_count*num_sample, replace = True))
        fwd_samples = list(fwd_starter_game_scores.sample(n=fwd_count*num_sample, replace = True))

        def_index_pos = 0
        mid_index_pos = 0
        fwd_index_pos = 0
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
            def_ww_pts = def_ww_samples[sample]
            total_pts += def_ww_pts

            def_index_pos = def_index_2
            mid_index_pos = mid_index_2
            fwd_index_pos = fwd_index_2

            def_formation_avg_game.append(total_pts)
        
        def_ww_win_percentage = get_win_percentage(def_formation_avg_game, formation_avg_game)
        def_ww_war = def_ww_win_percentage - 0.5
        print('Mean def ww game score: ', np.mean(def_formation_avg_game))
        print('std def ww game score: ', np.std(def_formation_avg_game))
        print("DEF avg war lost: ", def_ww_war)

        ## MID
        
        def_count = def_formation_count
        mid_count = mid_formation_count - 1
        fwd_count = fwd_formation_count

        mid_ww_samples = list(mid_ww_game_scores.sample(n=num_sample, replace = True))
 
        def_samples = list(def_starter_game_scores.sample(n=def_count*num_sample, replace = True))
        mid_samples = list(mid_starter_game_scores.sample(n=mid_count*num_sample, replace = True))
        fwd_samples = list(fwd_starter_game_scores.sample(n=fwd_count*num_sample, replace = True))

        def_index_pos = 0
        mid_index_pos = 0
        fwd_index_pos = 0
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
            mid_ww_pts = mid_ww_samples[sample]
            total_pts += mid_ww_pts

            def_index_pos = def_index_2
            mid_index_pos = mid_index_2
            fwd_index_pos = fwd_index_2

            mid_formation_avg_game.append(total_pts)

        mid_ww_win_percentage = get_win_percentage(mid_formation_avg_game, formation_avg_game)
        mid_ww_war = mid_ww_win_percentage - 0.5
        print('Mean mid ww game score: ', np.mean(mid_formation_avg_game))
        print('std mid ww game score: ', np.std(mid_formation_avg_game))
        print("MID avg war lost: ", mid_ww_war)
        ## FWD

        def_count = def_formation_count
        mid_count = mid_formation_count
        fwd_count = fwd_formation_count - 1

        fwd_ww_samples = list(fwd_ww_game_scores.sample(n=num_sample, replace = True))
 
        def_samples = list(def_starter_game_scores.sample(n=def_count*num_sample, replace = True))
        mid_samples = list(mid_starter_game_scores.sample(n=mid_count*num_sample, replace = True))
        fwd_samples = list(fwd_starter_game_scores.sample(n=fwd_count*num_sample, replace = True))

        def_index_pos = 0
        mid_index_pos = 0
        fwd_index_pos = 0
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
            fwd_ww_pts = fwd_ww_samples[sample]
            total_pts += fwd_ww_pts

            def_index_pos = def_index_2
            mid_index_pos = mid_index_2
            fwd_index_pos = fwd_index_2

            fwd_formation_avg_game.append(total_pts)

        fwd_ww_win_percentage = get_win_percentage(fwd_formation_avg_game, formation_avg_game)
        fwd_ww_war = fwd_ww_win_percentage - 0.5
        print('Mean fwd ww game score: ', np.mean(fwd_formation_avg_game))
        print('std fwd ww game score: ', np.std(fwd_formation_avg_game))
        print("FWD avg war lost: ", fwd_ww_war)   
        
        def_avg_game = def_avg_game + def_formation_avg_game
        mid_avg_game = mid_avg_game + mid_formation_avg_game
        fwd_avg_game = fwd_avg_game + fwd_formation_avg_game

    end = time.time()
    print(end - start)
    print("----------------------------")
    print("Overall average game mean: ", np.mean(avg_game))
    print("Overall average game std: ", np.std(avg_game))
    
    print("UNSHUFFLED")

    def_ww_win_percentage = get_win_percentage(def_avg_game, avg_game)
    def_ww_war = def_ww_win_percentage - 0.5
    print('Mean def ww game score: ', np.mean(def_avg_game))
    print('std def ww game score: ', np.std(def_avg_game))
    print("DEF avg war lost: ", def_ww_war)

    mid_ww_win_percentage = get_win_percentage(mid_avg_game, avg_game)
    mid_ww_war = mid_ww_win_percentage - 0.5
    print('Mean mid ww game score: ', np.mean(mid_avg_game))
    print('std mid ww game score: ', np.std(mid_avg_game))
    print("MID avg war lost: ", mid_ww_war)

    fwd_ww_win_percentage = get_win_percentage(fwd_avg_game, avg_game)
    fwd_ww_war = fwd_ww_win_percentage - 0.5
    print('Mean fwd ww game score: ', np.mean(fwd_avg_game))
    print('std fwd ww game score: ', np.std(fwd_avg_game))
    print("FWD avg war lost: ", fwd_ww_war)   

    print("FWD avg war lost: ", fwd_ww_war)   

    print("----------------------------")
    print("SHUFFLED")
    
    random.shuffle(avg_game)

    def_ww_win_percentage = get_win_percentage(def_avg_game, avg_game)
    def_ww_war = def_ww_win_percentage - 0.5
    print('Mean def ww game score: ', np.mean(def_avg_game))
    print('std def ww game score: ', np.std(def_avg_game))
    print("DEF avg war lost: ", def_ww_war)

    mid_ww_win_percentage = get_win_percentage(mid_avg_game, avg_game)
    mid_ww_war = mid_ww_win_percentage - 0.5
    print('Mean mid ww game score: ', np.mean(mid_avg_game))
    print('std mid ww game score: ', np.std(mid_avg_game))
    print("MID avg war lost: ", mid_ww_war)

    fwd_ww_win_percentage = get_win_percentage(fwd_avg_game, avg_game)
    fwd_ww_war = fwd_ww_win_percentage - 0.5
    print('Mean fwd ww game score: ', np.mean(fwd_avg_game))
    print('std fwd ww game score: ', np.std(fwd_avg_game))
    print("FWD avg war lost: ", fwd_ww_war)   

    ## For all players SAMPLING procedure
    player_dict = {}
    for index, row in xfpts_df.iterrows():
        print(index)
        sim_games = []
        player = row['Player']
        pos = row['Position']
        games = row['n']
        player_weekly_pts = weekly_xfpts_df.loc[(weekly_xfpts_df['Player'] == player)]['xFpts']
        
        for formation in formation_list:
        
            def_count = def_formation_count
            mid_count = mid_formation_count
            fwd_count = fwd_formation_count
            if pos == 'D':
                def_count -= 1
                ww_war = def_ww_war
            elif pos == 'M':
                mid_count -= 1
                ww_war = mid_ww_war
            elif pos == 'F':
                fwd_count -= 1
                ww_war = fwd_ww_war
            
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
        
        win_percentage = get_win_percentage(sim_games, avg_game)
        player_war = win_percentage - 0.5
        games_missed = 38 - games
        total_war_won = player_war * games
        total_ww_war_lost = ww_war * games_missed
        total_player_war = total_war_won + total_ww_war_lost
        player_dict[player] = [pos, games, games_missed, player_war, total_war_won, ww_war, total_ww_war_lost, ww_war * 38, total_player_war, total_player_war - (ww_war * 38)]

    ## convert player dict to pandas df
    df = pd.DataFrame.from_dict(player_dict, orient='index', columns = ['Pos', 'games_played', 'games_missed', 'pWAS', 'pWAS_earned', 'pos_pWAS_lost', 'total_pWAS_lost', 'season_ww_pWAS_lost', 'net_pWAS', 'pWAS_over_ww'])

    df = df.sort_values(by = 'net_pWAS', ascending = False)

    df.to_csv("new_positions_results/pwas.def_{}.mid_{}.for_{}.{}_samples.csv".format(def_num, mid_num, fwd_num, num_sample))

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
            
