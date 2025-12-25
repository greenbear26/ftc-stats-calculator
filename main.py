import request
import numpy as np

def main():
    eventCode = "USMAREQ"
    season = 2025
    matches = request.get_qual_matches(eventCode, season)
    # print(matches)
    teams = request.get_teams(eventCode, season)
    # print(teams)

    matches_matrix = np.zeros((len(matches)*2, len(teams)))
    scores = np.zeros(len(matches))
    print(scores)
    # for match_index, match in enumerate(matches):
    #     red_score = match['scores']['red']['totalPointsNp']
    #     blue_score = match['scores']['blue']['totalPointsNp']
    #     scores.append((red_score, blue_score))
    #     for alliance in match['teams']:
    #         team_number = alliance['teamNumber']
    #         team_index = teams.index(team_number)
    #         if alliance['alliance'] == 'RED':
    #             matches_matrix[match_index*2][team_index] = 1
    #             matches_matrix[match_index*2+1][team_index] = 0
    #         else:
    #             matches_matrix[match_index*2][team_index] = 0
    #             matches_matrix[match_index*2+1][team_index] = 1
    print(matches_matrix)




if __name__ == "__main__":
    main()
