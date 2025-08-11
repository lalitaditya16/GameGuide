import requests

class SteamClient:
    BASE_URL = "https://api.steampowered.com"

    def __init__(self, api_key=None):
        self.api_key = api_key

    def get_game_name(self, appid):
        """
        Fetches the game's name from the Steam store API using the appid.
        """
        try:
            store_url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
            r = requests.get(store_url, timeout=5)
            r.raise_for_status()
            data = r.json()

            if str(appid) in data and data[str(appid)].get("success"):
                return data[str(appid)]["data"].get("name", "Unknown Game")
            return "Unknown Game"
        except Exception:
            return "Unknown Game"

    def get_most_played_games(self, limit=10):
        """
        Fetches the most played games from Steam, with names and current players.
        """
        endpoint = f"{self.BASE_URL}/ISteamChartsService/GetMostPlayedGames/v1/"

        try:
            response = requests.get(endpoint, timeout=5)
            response.raise_for_status()
            data = response.json()

            games = data.get("response", {}).get("ranks", [])
            result = []

            for game in games[:limit]:
                appid = game.get("appid")
                name = self.get_game_name(appid)
                current_players = game.get("concurrent_in_game", 0) or 0

                result.append({
                    "appid": appid,
                    "name": name,
                    "current_players": current_players
                })

            return result

        except Exception as e:
            print(f"Error fetching most played games: {e}")
            return []
