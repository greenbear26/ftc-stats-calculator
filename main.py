import request
import numpy as np
import pandas as pd

def main():
    eventCode = "USMAREQ"
    season = 2025
    matches = request.get_qual_matches(eventCode, season)
    teams = request.get_teams(eventCode, season)

    matches_matrix = np.zeros((len(matches)*2, len(teams)))
    offense_scores = np.zeros(len(matches)*2)
    defense_scores = np.zeros(len(matches)*2)
    for match_index, match in enumerate(matches):
        red_score = match['scores']['red']['totalPointsNp']
        blue_score = match['scores']['blue']['totalPointsNp']
        for team in match['teams']:
            team_number = team['teamNumber']
            team_index = teams.index(team_number)
            if team['alliance'] == 'Red':
                matches_matrix[match_index*2][team_index] = 1
                offense_scores[match_index*2] = red_score
                defense_scores[match_index*2] = blue_score
            else:
                matches_matrix[match_index*2+1][team_index] = 1
                offense_scores[match_index*2+1] = blue_score
                defense_scores[match_index*2+1] = red_score

    opr = np.linalg.lstsq(matches_matrix, offense_scores, rcond=None)[0]
    opr = np.round(opr, 2)
    dpr = np.linalg.lstsq(matches_matrix, defense_scores, rcond=None)[0]
    dpr = np.round(dpr, 2)
    ccwm = opr - dpr

    team_frame = pd.DataFrame({
        'Team': teams,
        'OPR': opr,
        'DPR': dpr,
        'CCWM': ccwm
    })
    print(team_frame.sort_values(by='DPR', ascending=True, ignore_index=True))

if __name__ == "__main__":
    main()
