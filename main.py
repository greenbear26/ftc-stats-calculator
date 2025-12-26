import request
import numpy as np
import pandas as pd
import sys

def main(eventCode, season):
    matches = request.get_qual_matches(eventCode, season)
    teams = request.get_teams(eventCode, season)

    matches_matrix = np.zeros((len(matches)*2, len(teams)))
    offense_scores = np.zeros(len(matches)*2)
    defense_scores = np.zeros(len(matches)*2)
    team_opponents = {team: [] for team in teams}
    for match_index, match in enumerate(matches):
        red_score = match['scores']['red']['totalPointsNp']
        blue_score = match['scores']['blue']['totalPointsNp']

        red_teams = [team['teamNumber'] for team in match['teams'] if
                     team['alliance'] == 'Red']
        blue_teams = [team['teamNumber'] for team in match['teams'] if
                      team['alliance'] == 'Blue']

        for team in match['teams']:
            team_number = team['teamNumber']
            team_index = teams.index(team_number)
            if team['alliance'] == 'Red':
                matches_matrix[match_index*2][team_index] = 1
                offense_scores[match_index*2] = red_score
                defense_scores[match_index*2] = blue_score
                team_opponents[team_number].extend(blue_teams)
            else:
                matches_matrix[match_index*2+1][team_index] = 1
                offense_scores[match_index*2+1] = blue_score
                defense_scores[match_index*2+1] = red_score
                team_opponents[team_number].extend(red_teams)


    opr = np.linalg.lstsq(matches_matrix, offense_scores, rcond=None)[0]
    opr = np.round(opr, 2)
    dpr = np.linalg.lstsq(matches_matrix, defense_scores, rcond=None)[0]
    dpr = np.round(dpr, 2)
    ccwm = opr - dpr

    avg_opponents_opr = []
    avg_opponents_dpr = []
    avg_opponents_ccwm = []
    for team in teams:
        opponents = team_opponents[team]
        if len(opponents) == 0:
            avg_opponents_opr.append(0)
            avg_opponents_dpr.append(0)
            avg_opponents_ccwm.append(0)
            continue
        opponent_indices = [teams.index(opponent) for opponent in opponents]
        avg_opponents_opr.append(np.round(np.mean(opr[opponent_indices]), 2))
        avg_opponents_dpr.append(np.round(np.mean(dpr[opponent_indices]), 2))
        avg_opponents_ccwm.append(np.round(np.mean(ccwm[opponent_indices]), 2))

    team_frame = pd.DataFrame({
        'Team': teams,
        'OPR': opr,
        'DPR': dpr,
        'CCWM': ccwm,
        'Avg Opp OPR': avg_opponents_opr,
        'Avg Opp DPR': avg_opponents_dpr,
        'Avg Opp CCWM': avg_opponents_ccwm
    })

    no_show_teams = [team for team in teams if
                     len(team_opponents[team]) == 0]
    team_frame = team_frame[~team_frame['Team'].isin(no_show_teams)]

    print(team_frame.sort_values(by='Avg Opp CCWM', ascending=False,
                                 ignore_index=True).head(50))

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage: python main.py <eventCode> <season>")
        sys.exit(1)
    eventCode = sys.argv[1]
    season = int(sys.argv[2])
    main(eventCode, season)
