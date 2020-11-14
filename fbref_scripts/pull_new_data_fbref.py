import sys
import pandas as pd
import time
from urllib.error import HTTPError
import json
import yaml
import getopt

accio_tables_string = "http://acciotables.herokuapp.com/?page_url="
table_selector_string = "&content_selector_id=%23"



def help(exit_num = 1):
    print("""-----------------------------------------------------------------
ARGUMENTS
    -c => <yaml> Config File REQUIRED
    -s => <string> string of the first gameweek to include in newly pulled data 
                    REQUIRED unless override is specified, in which case pull all data
    --override <boolean> pull all data OPTIONAL
""")
    sys.exit(exit_num)


def main(argv): 
    try: 
        opts, args = getopt.getopt(sys.argv[1:], "c:s:", ['override']) 

    except getopt.GetoptError:
        print("Error: Incorrect usage of getopts flags!")
        help() 

    options_dict = dict(opts)
    
    ## Required arguments
    try:
        config_file = options_dict['-c']

    except KeyError:
        print("Error: One of your required arguments does not exist.")
        help()

    first_week_string = options_dict.get('-s', False)
    override = options_dict.get('--override', False)
    if override == '':
        override = True

    if not override:
        if not first_week_string:
            print("Error: Need to specify a first week string")
            help()


    print("Acceptable Inputs Given")

    driver(config_file, first_week_string, override)

def driver(config_file, first_week_string, override):

    config_dict = yaml.load(open(config_file, 'r'), Loader=yaml.SafeLoader)

    match_url_file = config_dict['match_url_file']
    fbref_tables_dict = config_dict['fbref_tables']
    team_id_file = config_dict['team_id_file']
    name_conversion_json = config_dict['name_conversion_file']

    ### Get the dict linking team id with team
    team_id_dict = get_team_id_dict(team_id_file)

    # iterate through list of matches in a season to get all the data for every player
    full_table_dict = pull_match_data(match_url_file, team_id_dict, first_week_string, override)

    # NEXT STEPS ARE TO CLEAN UP DATA

    ## open name conversion dict
    with open(name_conversion_json, 'r') as j_file:
        name_conversion_dict = json.load(j_file)

    check_players_to_change(name_conversion_dict, full_table_dict)

    # clean the data and append to the master file
    for table_type in ['summary', 'passing', 'passing_types', 'defense', 'possession', 'misc']:
        
        df = full_table_dict[table_type]
        new_df = df.replace(name_conversion_dict)
        convert_dates(new_df)

        master_file = fbref_tables_dict[table_type]

        if override:
            new_df.to_csv(master_file)
        else:
            with open(master_file, 'a') as f:
                f.write('\n')
            new_df.to_csv(master_file, mode='a', header=False)









def pull_match_data(match_url_file, team_id_dict, first_week_string, override):

    start_matching = False
    if override:
        start_matching = True

    count = 0  

    ## saving each table individually
    summary_table_df = None
    passing_table_df = None
    passing_types_table_df = None
    defense_table_df = None
    possession_table_df = None
    misc_table_df = None

    full_table_dict = {'summary': summary_table_df,
                   'passing': passing_table_df,
                   'passing_types': passing_types_table_df,
                   'defense': defense_table_df,
                   'possession': possession_table_df,
                   'misc': misc_table_df}
    
    match_urls = open(match_url_file, 'r')
    for match_url in match_urls:

        match_url = match_url.strip()
        match_url_list = match_url.split('/')

        if not start_matching:
            if match_url_list[-1] == first_week_string:
                start_matching = True
            else:
                continue
        count += 1
        ## first identify teams playing
        home_team, away_team, date = get_overall_match_info(match_url_list[-1], team_id_dict)
        ## construct the base url to query
        base_url = accio_tables_string + match_url + table_selector_string
        for team in [home_team, away_team]:
            team_id, team_string = team_id_dict[team]
            # get the opponent
            opponent_team_string = team_id_dict[home_team][1]
            if team == home_team:
                opponent_team_string = team_id_dict[away_team][1]
            
            for table_type in ['summary', 'passing', 'passing_types', 'defense', 'possession', 'misc']:
                #print(table_type)
                # don't want to overburden the system
                time.sleep(2)
                
                full_table_df = full_table_dict[table_type]
                #print(full_table_df)
                table_id_string = 'stats_' + team_id + '_' + table_type
                table_url = str(base_url + table_id_string)
            
                # get summary table
                http_error = True
                while http_error:
                    try:
                        team_table_df = pd.read_html(table_url, header=1)[0]
                        http_error = False
                    except HTTPError:
                        # if there happens to be an html error, then wait 30 seconds and try again
                        print('Html error! Waiting 30 seconds and trying again...')
                        time.sleep(5)
                
                team_table_df.drop(team_table_df.tail(1).index,inplace=True)
            
                # add date column
                team_table_df['Date'] = [date] * len(team_table_df)
                team_table_df['Team'] = [team_string] * len(team_table_df)
                team_table_df['Opponent'] = [opponent_team_string] * len(team_table_df)
            
                try:
                    full_table_df = full_table_df.append(team_table_df, ignore_index = True)
                except AttributeError:
                    full_table_df = team_table_df
                #if table_type == 'summary':
                #        print(full_table_df)
                full_table_dict[table_type] = full_table_df
        print(count)
    ## run some qc
    if not start_matching:
        print("Error: Never found match of interest")
        help()

    return full_table_dict

def check_players_to_change(name_conversion_dict, full_table_dict):

    # Find the players whose names need to be converted in the name conversion json
    fantrax_file_19_20 = "/Users/adamscj/Documents/GitHub/overthinking_football/data/fantrax_data/fantrax.weekly.all_data_combined.no_double_gws.new_positions.csv"
    fantrax_file_20_21 ="/Users/adamscj/Documents/GitHub/overthinking_football/data/fantrax_data/2020_2021_data/fantrax.weekly.no_double_gws.20_21.csv"

    players_19_20 = list(pd.read_csv(fantrax_file_19_20)['Player'])
    players_20_21 = list(pd.read_csv(fantrax_file_20_21)['Player'])
    #print(players_19_20)
    missing_player = []
    summary_table = full_table_dict['summary']
    player_count = -1
    for player in summary_table['Player']:
        player_count += 1
        if player not in name_conversion_dict and player not in players_19_20 and player not in players_20_21:
            player_pos = summary_table['Pos'][player_count]
            print(player_pos)
            if player_pos == 'GK':
                continue
            if player not in missing_player:
                missing_player.append(player)

    if len(missing_player) >= 1:
        print(missing_player)
        print("Exiting script now, too many missing players. Go back and fix!")
        help()

def get_overall_match_info(match_url, team_id_dict):
    
    teams_found = []
    
    # could be more efficient...but only dealing with 20 teams
    for team in team_id_dict:
        if team in match_url:
            teams_found.append(team)
    
    # check that the appropriate number of teams have been identified in url
    if len(teams_found) != 2:
        print("Error: Improper number of teams found in url")
        print(teams_found)
        print(match_url_list)
        return False
    
    ## id home and away teams and the date
    
    if '-'.join(teams_found) in match_url:
        # implies the proper order
        pass
        
    elif '-'.join(teams_found[::-1]) in match_url:
        # swap the order
        teams_found = teams_found[::-1]

    else:
        print("Error: url format assumptions are wrong")
        return False
    
    # next get the date
    date = get_date_from_url(teams_found, match_url)
    
    return teams_found + [date]

def get_date_from_url(teams_found, match_url):
    
    # I'm assuming the following format:
    # */HOMETEAM-AWAYTEAM-MONTH-DAY-YEAR-LEAGUE
    # e.g */Aston-Villa-Manchester-United-July-9-2020-Premier-League
    
    teams_string_length = len(teams_found[0]) + len(teams_found[1]) + 2
    date_and_league_string = match_url[teams_string_length:]
    date_list = date_and_league_string.strip().split('-')[0:3]
    
    date = '-'.join(date_list)
    
    return date


def get_team_id_dict(team_id_file):
    
    team_id_dict = {}

    with open(team_id_file, 'r') as team_id_csv:
        for line in team_id_csv:
            team, id_string, table_team_string = line.strip().split(',')
            team_id_dict[team] = [id_string, table_team_string]

    return team_id_dict

def convert_dates(df):
    converted_date_column = []
    for date in df['Date']:

        new_date = date.replace('2019', '19')
        new_date = new_date.replace('2020', '20')

        new_date = new_date.replace('-1-', '-01-')
        new_date = new_date.replace('-2-', '-02-')
        new_date = new_date.replace('-3-', '-03-')
        new_date = new_date.replace('-4-', '-04-')
        new_date = new_date.replace('-5-', '-05-')
        new_date = new_date.replace('-6-', '-06-')
        new_date = new_date.replace('-7-', '-07-')
        new_date = new_date.replace('-8-', '-08-')
        new_date = new_date.replace('-9-', '-09-')

        new_date = new_date.replace('January', '01')
        new_date = new_date.replace('February', '02')
        new_date = new_date.replace('March', '03')
        new_date = new_date.replace('April', '04')
        new_date = new_date.replace('May', '05')
        new_date = new_date.replace('June', '06')
        new_date = new_date.replace('July', '07')
        new_date = new_date.replace('August', '08')
        new_date = new_date.replace('September', '09')
        new_date = new_date.replace('October', '10')
        new_date = new_date.replace('November', '11')
        new_date = new_date.replace('December', '12')

        new_date = new_date.replace('-', '/')

        converted_date_column.append(new_date)
    
    df['Date'] = converted_date_column
    


if __name__ == "__main__":
    main(sys.argv[1:])
