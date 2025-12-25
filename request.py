import requests

URL = "https://api.ftcscout.org/graphql"
def make_request(eventCode, season) -> dict:
    """Makes a POST request to the GraphQL API to fetch match data for a given
    event code and season.

    Params:
        eventCode (str): The event code to query.
        season (int): The season year to query.
    Returns:
        dict: The JSON response from the API.
    """

    query = f"""
        query Query($season: Int!, $code: String!) {{
          eventByCode(season: $season, code: $code) {{
            matches {{
              scores {{
                ... on MatchScores2025 {{
                  red {{
                    totalPointsNp
                  }}
                  blue {{
                    totalPointsNp
                  }}
                }}
              }}
              teams {{
                alliance
                teamNumber
              }}
              tournamentLevel
            }}
            teams {{
              teamNumber
            }}
          }}
        }}
    """

    variables = {
      "season": season,
      "code": eventCode
    }

    # Data to be sent in the request body
    payload = {
        "query": query,
        "variables": variables
    }

    data = None
    try:
        # Make the POST request with JSON data
        response = requests.post(URL, json=payload)

        # Check if the request was successful (status code 201 Created)
        if response.status_code == 200:
            data = response.json()
            print("POST Request Successful:")
        else:
            print(f"Error: {response.status_code}")

        return data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def get_qual_matches(eventCode, season) -> list:
    """Fetches qualification matches for a given event code and season.
    
    Params:
        eventCode (str): The event code to query.
        season (int): The season year to query.
    Returns:
        list: A list of qualification matches, in dictionary format.
    """

    matches = make_request(eventCode, season).get("data", {})\
        .get("eventByCode", {}).get("matches", [])

    qual_matches = [match for match in matches if match.get("tournamentLevel")
        == "Quals"]
    return qual_matches

def get_teams(eventCode, season) -> list:
    """Fetches teams for a given event code and season.
    
    Params:
        eventCode (str): The event code to query.
        season (int): The season year to query.
    Returns:
        list: A list of teams, by team number
    """

    teams_list = make_request(eventCode, season).get("data", {})\
        .get("eventByCode", {}).get("teams", [])

    teams = [team.get("teamNumber") for team in teams_list]
    
    return teams
