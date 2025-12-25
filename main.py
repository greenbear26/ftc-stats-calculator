import request
import numpy as np

def main():
    eventCode = "USMAREQ"
    season = 2025
    matches = request.get_qual_matches(eventCode, season)
    teams = request.get_teams(eventCode, season)

    matches_matrix = np.zeros((len(matches)*2, len(teams)))
    scores = np.zeros(len(matches)*2)
    for match_index, match in enumerate(matches):
        red_score = match['scores']['red']['totalPointsNp']
        blue_score = match['scores']['blue']['totalPointsNp']
        for team in match['teams']:
            team_number = team['teamNumber']
            team_index = teams.index(team_number)
            if team['alliance'] == 'Red':
                matches_matrix[match_index*2][team_index] = 1
                scores[match_index*2] = red_score
            else:
                matches_matrix[match_index*2+1][team_index] = 1
                scores[match_index*2+1] = blue_score

    opr = np.linalg.lstsq(matches_matrix, scores, rcond=None)[0]
    for team_index, team_number in enumerate(teams):
        print(f"Team {team_number}: {opr[team_index]:.2f} OPR")



if __name__ == "__main__":
    main()
