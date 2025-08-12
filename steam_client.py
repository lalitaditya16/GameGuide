# steam_client.py
import requests
from bs4 import BeautifulSoup
import re
import time

class SteamClient:
    BASE_URL = "https://api.steampowered.com"

    def __init__(self, api_key=None, session=None):
        """
        api_key is optional (Steam Web API key). Many endpoints used here do not strictly require a key,
        but you can pass it if you have one.
        """
        self.api_key = api_key
        self.session = session or requests.Session()
        # Friendly User-Agent so Steam doesn't reject scraping calls
        self.session.headers.update({
            "User-Agent": "GameGuide/1.0 (+https://example.com)"
        })

    def get_app_details(self, appid):
        """
        Use Steam Store API to get app details (name, is_free, price_overview).
        Returns dict or None.
        """
        try:
            url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&l=en"
            r = self.session.get(url, timeout=6)
            r.raise_for_status()
            payload = r.json()
            app_entry = payload.get(str(appid))
            if not app_entry or not app_entry.get("success"):
                return None
            data = app_entry["data"]
            return {
                "name": data.get("name"),
                "is_free": data.get("is_free", False),
                "price_overview": data.get("price_overview"),  # may be None for free apps
                "type": data.get("type"),
                "short_description": data.get("short_description")
            }
        except Exception:
            return None

    def get_game_name(self, appid):
        """Fallback: get the name via store API (wrapper)."""
        d = self.get_app_details(appid)
        if d:
            return d.get("name") or "Unknown Game"
        return "Unknown Game"

    def get_current_players(self, appid):
        """Get current player count using the Steam Web API (no key required for this method)."""
        try:
            url = f"{self.BASE_URL}/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
            params = {"appid": appid}
            # If user provided an API key, include it (harmless)
            if self.api_key:
                params["key"] = self.api_key
            r = self.session.get(url, params=params, timeout=6)
            r.raise_for_status()
            payload = r.json()
            return payload.get("response", {}).get("player_count")
        except Exception:
            return None

    def get_peak_players(self, appid):
        """Scrape steamcharts.com for today's peak number (best-effort)."""
        try:
            charts_url = f"https://steamcharts.com/app/{appid}"
            r = self.session.get(charts_url, timeout=6)
            r.raise_for_status()
            text = r.text

            # Try HTML parse first
            soup = BeautifulSoup(text, "html.parser")
            stats = soup.find_all("div", class_="app-stat")
            for stat in stats:
                if "Peak Today" in stat.text:
                    span = stat.find("span", class_="num")
                    if span and span.text:
                        return int(span.text.strip().replace(",", ""))

            # Fallback to regex search around the "Peak Today" phrase
            idx = text.find("Peak Today")
            if idx != -1:
                snippet = text[idx: idx + 150]
                m = re.search(r"(\d{1,3}(?:,\d{3})*)", snippet)
                if m:
                    return int(m.group(1).replace(",", ""))

        except Exception:
            pass
        return None

    def get_most_played_games(self, limit=10, free_only=None):
        """
        Return a list of dicts with keys:
         - appid (int)
         - name (str)
         - current_players (int or None)
         - peak_players (int or None)
         - is_free (bool)
         - price (float in USD or None)
        free_only: True => only free games, False => only paid games, None => both
        """
        url = f"{self.BASE_URL}/ISteamChartsService/GetMostPlayedGames/v1/"
        try:
            r = self.session.get(url, timeout=6)
            r.raise_for_status()
            payload = r.json()
            ranks = payload.get("response", {}).get("ranks", []) or []
        except Exception:
            ranks = []

        results = []
        # iterate through the ranks, gather details until we have `limit` entries matching filter
        for entry in ranks:
            if len(results) >= limit:
                break

            appid = entry.get("appid") or entry.get("app_id")
            if not appid:
                continue

            # The charts endpoint sometimes uses different field names; try a few
            current_raw = entry.get("concurrent") or entry.get("concurrent_in_game") or entry.get("current") or entry.get("players") or entry.get("count")
            current_players = None
            if isinstance(current_raw, (int, float)):
                current_players = int(current_raw)
            else:
                # we'll lazily fetch from the Steam API if the rank entry doesn't include a numeric
                current_players = None

            # app details from store
            details = self.get_app_details(appid)
            # if no store data, still try name fallback
            if details is None:
                name = self.get_game_name(appid)
                is_free = False
                price = None
            else:
                name = details.get("name") or self.get_game_name(appid)
                is_free = details.get("is_free", False)
                po = details.get("price_overview")
                if po and isinstance(po, dict):
                    # price is in cents
                    price = po.get("final") / 100.0 if po.get("final") is not None else None
                else:
                    price = 0.0 if is_free else None

            # apply free/paid filter
            if free_only is True and not is_free:
                continue
            if free_only is False and is_free:
                continue

            # ensure we have a current players integer (try fallback)
            if current_players is None:
                current_players = self.get_current_players(appid)

            peak_players = self.get_peak_players(appid)

            results.append({
                "appid": int(appid),
                "name": name,
                "current_players": int(current_players) if isinstance(current_players, (int, float)) else None,
                "peak_players": int(peak_players) if isinstance(peak_players, (int, float)) else None,
                "is_free": bool(is_free),
                "price": float(price) if isinstance(price, (int, float)) else price,
            })

        return results

    # convenience wrappers (they call get_most_played_games)
    def get_top_free_games(self, limit=10):
        return self.get_most_played_games(limit=limit, free_only=True)

    def get_top_paid_games(self, limit=10):
        return self.get_most_played_games(limit=limit, free_only=False)
    def get_peak_players_by_year(self, year, limit=10):
        """
        Get the top games released in a given year sorted by peak players.
        This is slower since it queries the Steam Store API for each app's release date.
        """
        try:
            # 1. Get the full app list from Steam
            applist_url = f"{self.BASE_URL}/ISteamApps/GetAppList/v2/"
            r = self.session.get(applist_url, timeout=10)
            r.raise_for_status()
            all_apps = r.json().get("applist", {}).get("apps", [])
        except Exception:
            return []

        results = []

        for app in all_apps:
            appid = app.get("appid")
            if not appid:
                continue

            details = self.get_app_details(appid)
            if not details:
                continue

            # Fetch release date from store API
            store_url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&l=en"
            try:
                store_data = self.session.get(store_url, timeout=6).json().get(str(appid), {}).get("data", {})
            except Exception:
                continue

            if not store_data or "release_date" not in store_data:
                continue

            release_info = store_data["release_date"]
            if release_info.get("coming_soon", True):
                continue

            release_date_str = release_info.get("date", "").strip()

            # Try parsing the release year
            release_year = None
            for fmt in ("%d %b, %Y", "%b %Y", "%Y"):
                try:
                    release_year = int(time.strptime(release_date_str, fmt).tm_year)
                    break
                except Exception:
                    continue

            if release_year != year:
                continue

            # Get peak players (scraped)
            peak_players = self.get_peak_players(appid)
            if not peak_players:
                continue

            results.append({
                "appid": appid,
                "name": details.get("name", "Unknown"),
                "peak_players": peak_players
            })

            # Optional: break early if results exceed some large number for speed
            if len(results) >= 200:
                break

        # Sort by peak players, descending
        results.sort(key=lambda x: x["peak_players"], reverse=True)

        return results[:limit]
