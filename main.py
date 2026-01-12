import request
import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt

def main(eventCode, season, sort_key, ascending):
    # Data Fetching
    matches = request.get_qual_matches(eventCode, season)
    teams = request.get_teams(eventCode, season)

    # Matrix Construction
    matches_matrix = np.zeros((len(matches)*2, len(teams)))
    offense_scores = np.zeros(len(matches)*2)
    defense_scores = np.zeros(len(matches)*2)
    team_opponents = {team: set() for team in teams}
    team_partners = {team: set() for team in teams}
    for match_index, match in enumerate(matches):
        red_score = match['scores']['red']['totalPointsNp']
        blue_score = match['scores']['blue']['totalPointsNp']

        red_teams = set([team['teamNumber'] for team in match['teams'] if
                     team['alliance'] == 'Red'])
        blue_teams = set([team['teamNumber'] for team in match['teams'] if
                      team['alliance'] == 'Blue'])

        for team in match['teams']:
            team_number = team['teamNumber']
            team_index = teams.index(team_number)
            if team['alliance'] == 'Red':
                matches_matrix[match_index*2][team_index] = 1
                offense_scores[match_index*2] = red_score
                defense_scores[match_index*2] = blue_score
                team_opponents[team_number].update(blue_teams)
                team_partners[team_number].update(red_teams - {team_number})
            else:
                matches_matrix[match_index*2+1][team_index] = 1
                offense_scores[match_index*2+1] = blue_score
                defense_scores[match_index*2+1] = red_score
                team_opponents[team_number].update(red_teams)
                team_partners[team_number].update(blue_teams - {team_number})

    # OPR/DPR/CCWM Calculation
    opr = np.linalg.lstsq(matches_matrix, offense_scores, rcond=None)[0]
    opr = np.round(opr, 2)
    dpr = np.linalg.lstsq(matches_matrix, defense_scores, rcond=None)[0]
    dpr = np.round(dpr, 2)
    ccwm = opr - dpr

    # Average Opponent Stats Calculation
    avg_opponents_opr = []
    avg_opponents_dpr = []
    avg_opponents_ccwm = []
    avg_partners_opr = []
    avg_partners_dpr = []
    avg_partners_ccwm = []
    for team in teams:
        opponents = team_opponents[team]
        if len(opponents) == 0:
            avg_opponents_opr.append(0)
            avg_opponents_dpr.append(0)
            avg_opponents_ccwm.append(0)
        else:
            opponent_indices = [teams.index(opponent) for opponent in opponents]
            avg_opponents_opr.append(np.round(np.mean(opr[opponent_indices]), 2))
            avg_opponents_dpr.append(np.round(np.mean(dpr[opponent_indices]), 2))
            avg_opponents_ccwm.append(np.round(np.mean(ccwm[opponent_indices]), 2))

        partners = team_partners[team]
        if len(partners) == 0:
            avg_partners_opr.append(0)
            avg_partners_dpr.append(0)
            avg_partners_ccwm.append(0)
        else:
            partner_indices = [teams.index(partner) for partner in partners]
            avg_partners_opr.append(np.round(np.mean(opr[partner_indices]), 2))
            avg_partners_dpr.append(np.round(np.mean(dpr[partner_indices]), 2))
            avg_partners_ccwm.append(np.round(np.mean(ccwm[partner_indices]), 2))

    # Data Presentation
    pd.set_option('display.max_rows', None)

    team_frame = pd.DataFrame({
        'Team': teams,
        'OPR': opr,
        'DPR': dpr,
        'CCWM': ccwm,
        'Avg Opp OPR': avg_opponents_opr,
        'Avg Opp DPR': avg_opponents_dpr,
        'Avg Opp CCWM': avg_opponents_ccwm,
        'Avg Partner OPR': avg_partners_opr,
        'Avg Partner DPR': avg_partners_dpr,
        'Avg Partner CCWM': avg_partners_ccwm
    })

    team_frame['OPRe'] = 2*team_frame['Avg Opp DPR'] \
        - team_frame['Avg Partner OPR']
    team_frame['DPRe'] = 2*team_frame['Avg Opp OPR'] \
        - team_frame['Avg Partner DPR']
    team_frame['CCWMe'] = team_frame['OPRe'] - team_frame['DPRe']
    team_frame['OPRreq'] = 2*team_frame['Avg Opp OPR'] \
        - team_frame['Avg Partner OPR']
    team_frame['DPRreq'] = 2*team_frame['Avg Opp DPR'] \
        - team_frame['Avg Partner DPR']
    team_frame['CCWMreq'] = 2*team_frame['Avg Opp CCWM'] \
        - team_frame['Avg Partner CCWM']
    team_frame['OPR - OPRe'] = (team_frame['OPR'] - team_frame['OPRe']).round(2)
    team_frame['DPR - DPRe'] = (team_frame['DPR'] - team_frame['DPRe']).round(2)
    team_frame['CCWM - CCWMe'] = (team_frame['CCWM'] - team_frame['CCWMe']).round(2)

    no_show_teams = [team for team in teams if
                     len(team_opponents[team]) == 0]
    team_frame = team_frame[~team_frame['Team'].isin(no_show_teams)]
    show_frame = team_frame[['Team', 'OPR', 'DPR', 'CCWM', 'OPRe', 'DPRe', 
                             'CCWMe', 'OPR - OPRe', 'DPR - DPRe', 'CCWM - CCWMe',
                             'OPRreq', 'DPRreq', 'CCWMreq']]

    # Sort and Print
    print(show_frame.sort_values(by=sort_key, ascending=ascending,
                                 ignore_index=True))
    print("\nValue Definitions:")
    print("OPR: Offensive Power Rating")
    print("DPR: Defensive Power Rating")
    print("CCWM: Calculated Contribution to Winning Margin")
    print("OPRe: Expected OPR based on opponents' DPR and partners' OPR")
    print("DPRe: Expected DPR based on opponents' OPR and partners' DPR")
    print("CCWMe: Expected CCWM based on OPERe and DPRe")
    print("OPR - OPRe: Difference between actual OPR and expected OPR")
    print("DPR - DPRe: Difference between actual DPR and expected DPR")
    print("CCWM - CCWMe: Difference between actual CCWM and expected CCWM")
    print("OPRreq: Minimum OPR to win based on opponents' OPR and partners' OPR")
    print("DPRreq: Maximum DPR to win based on opponents' DPR and partners' DPR")
    print("CCWMreq: Minimum CCWM to win based on opponents' CCWM and partners' CCWM")
    # Event Averages
    # print(f"\nEvent Average OPR: {team_frame['OPR'].mean():.2f}")

    # # Graph
    # max_data = team_frame[team_frame.index >= min_team_index].head(10)

    # ax = max_data.plot(x='Team', y=team_frame.columns[1:], kind='bar')

    # ax.title.set_text(f'Team Stats for Event {eventCode} ({season})')

    # plt.show()



if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <eventCode> <season> optional: <sort_key> <ascending>")
        sys.exit(1)
    eventCode = sys.argv[1]
    season = int(sys.argv[2])
    sort_key = sys.argv[3] if len(sys.argv) > 3 else 'OPR'
    ascending = sys.argv[4].lower() == 'true' if len(sys.argv) > 4 else False
    main(eventCode, season, sort_key, ascending)
