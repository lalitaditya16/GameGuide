import requests
class SteamClient:
    BASE_URL = "https://api.steampowered.com"

    def __init__(self, api_key=None):  # Make API key optional
        self.api_key = api_key

    def get_most_played_games(self, limit=10):
        endpoint = f"{self.BASE_URL}/ISteamChartsService/GetMostPlayedGames/v1/"
        response = requests.get(endpoint)
        response.raise_for_status()
        data = response.json()
        games = data.get("response", {}).get("ranks", [])
        return games[:limit]
