start_string=$1
output_file=$2

rules_yaml="/Users/adamscj/Documents/GitHub/overthinking_football/fantrax_scripts/20_21_standard_rules.yaml"
gw_data="/Users/adamscj/Documents/GitHub/overthinking_football/data/fantrax_data/2020_2021_data/fantrax.weekly.no_double_gws.20_21.csv"
fbref_xdata="/Users/adamscj/Documents/GitHub/overthinking_football/data/fbref/premier_league/20_21/master.name_cleaned.summary_table.csv"
match_total_data="/Users/adamscj/Documents/GitHub/overthinking_football/data/fbref/premier_league/20_21/matches_xg_data_20_21.csv"
python3 /Users/adamscj/Documents/GitHub/overthinking_football/fbref_scripts/pull_new_data_fbref.py -c /Users/adamscj/Documents/GitHub/overthinking_football/data/fbref/premier_league/20_21/20_21_fbref_config.yaml -s $start_string
python3 /Users/adamscj/Documents/GitHub/overthinking_football/fantrax_scripts/calculate_xfpts.py \
    -r $rules_yaml \
    -w $gw_data \
    -x $fbref_xdata \
    -c $match_total_data \
    -o $output_file

