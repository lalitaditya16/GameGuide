import requests

class SteamClient:
    BASE_URL = "https://api.steampowered.com"

    def __init__(self, api_key=None):
        self.api_key = api_key

    def get_most_played_games(self, limit=10):
        """
        Fetches the most played games from Steam and returns a list of dicts with appid, name, and current players.
        """
        endpoint = f"{self.BASE_URL}/ISteamChartsService/GetMostPlayedGames/v1/"

        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()

            games = data.get("response", {}).get("ranks", [])
            result = []
            for game in games[:limit]:
                appid = game.get("appid")
                name = game.get("name", "Unknown Game")
                current_players = game.get("concurrent_in_game", 0) or 0  # Ensure it's never None

                result.append({
                    "appid": appid,
                    "name": name,
                    "current_players": current_players
                })

            return result

        except Exception as e:
            print(f"Error fetching most played games: {e}")
            return []
