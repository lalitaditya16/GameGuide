import requests
from bs4 import BeautifulSoup
import re

class SteamClient:
    BASE_URL = "https://api.steampowered.com"

    def __init__(self, api_key=None):
        self.api_key = api_key

    def get_game_name(self, appid):
        """Get the game's name from Steam Store."""
        try:
            store_url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
            r = requests.get(store_url, timeout=5)
            r.raise_for_status()
            data = r.json()
            if str(appid) in data and data[str(appid)].get("success"):
                return data[str(appid)]["data"].get("name", "Unknown Game")
        except Exception:
            pass
        return "Unknown Game"

    def get_current_players(self, appid):
        """Get current player count from Steam API."""
        try:
            url = f"{self.BASE_URL}/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
            params = {"appid": appid}
            r = requests.get(url, params=params, timeout=5)
            r.raise_for_status()
            data = r.json()
            return data.get("response", {}).get("player_count", None)
        except Exception:
            return None

    def get_peak_players(self, appid):
        """
        Get daily peak players from SteamCharts by scraping the HTML.
        """
        try:
            charts_url = f"https://steamcharts.com/app/{appid}"
            r = requests.get(charts_url, timeout=5)
            r.raise_for_status()

            soup = BeautifulSoup(r.text, "html.parser")
            stats = soup.find_all("div", class_="app-stat")

            for stat in stats:
                if "Peak Today" in stat.text:
                    peak_text = stat.find("span", class_="num").text.strip()
                    return int(peak_text.replace(",", ""))
        except Exception:
            pass
        return None

    def get_most_played_games(self, limit=10):
        """Get most played games with name, current, and peak players."""
        endpoint = f"{self.BASE_URL}/ISteamChartsService/GetMostPlayedGames/v1/"
        try:
            r = requests.get(endpoint, timeout=5)
            r.raise_for_status()
            data = r.json()
            games = data.get("response", {}).get("ranks", [])
            result = []
            for game in games[:limit]:
                appid = game.get("appid")
                name = self.get_game_name(appid)
                current_players = self.get_current_players(appid)
                peak_players = self.get_peak_players(appid)
                result.append({
                    "appid": appid,
                    "name": name,
                    "current_players": current_players,
                    "peak_players": peak_players
                })
            return result
        except Exception as e:
            print(f"Error fetching most played games: {e}")
            return []

    def get_top_free_games(self, limit=10):
        """Get top free-to-play games from Steam search page."""
        url = "https://store.steampowered.com/search/?filter=free&sort_by=ConcurrentUsers_DESC"
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            games = []

            for item in soup.select(".search_result_row")[:limit]:
                title = item.select_one(".title").text.strip()
                link = item["href"]
                appid = link.split("/app/")[1].split("/")[0]
                games.append({
                    "appid": appid,
                    "name": title,
                    "url": link,
                    "current_players": self.get_current_players(appid),
                    "peak_players": self.get_peak_players(appid)
                })

            return games
        except Exception as e:
            print("Error fetching free games:", e)
            return []

    def get_top_paid_games(self, limit=10):
        """Get top paid games from Steam search page."""
        url = "https://store.steampowered.com/search/?sort_by=ConcurrentUsers_DESC&maxprice=999999&filter=topsellers"
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            games = []

            for item in soup.select(".search_result_row")[:limit]:
                title = item.select_one(".title").text.strip()
                link = item["href"]
                appid = link.split("/app/")[1].split("/")[0]
                games.append({
                    "appid": appid,
                    "name": title,
                    "url": link,
                    "current_players": self.get_current_players(appid),
                    "peak_players": self.get_peak_players(appid)
                })

            return games
        except Exception as e:
            print("Error fetching paid games:", e)
            return []
