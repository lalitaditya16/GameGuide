
"""
RAWG API Client Wrapper
=======================

A comprehensive Python client for interacting with the RAWG Video Games Database API.
Handles authentication, request management, caching, error handling, and rate limiting.
"""

import requests
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import streamlit as st
from functools import wraps
import logging
from urllib.parse import urljoin, urlencode

from config import config, API_ENDPOINTS, ERROR_MESSAGES

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAWGAPIError(Exception):
    """Custom exception for RAWG API errors."""
    pass

class RateLimitError(RAWGAPIError):
    """Exception raised when API rate limit is exceeded."""
    pass

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry API calls on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, RAWGAPIError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed.")
            raise last_exception
        return wrapper
    return decorator

class RAWGClient:
    """
    RAWG API Client for interacting with the RAWG Video Games Database.

    This client provides methods to fetch games, developers, publishers, platforms,
    genres, and other gaming-related data from the RAWG API.
    """

    def __init__(self, api_key: str, base_url: str = None, user_agent: str = None):
        """
        Initialize the RAWG API client.

        Args:
            api_key (str): Your RAWG API key
            base_url (str, optional): Base URL for the API
            user_agent (str, optional): User agent string
        """
        self.api_key = api_key
        self.base_url = base_url or config.rawg_base_url
        self.user_agent = user_agent or config.user_agent
        self.session = requests.Session()

        # Set up session headers
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # Minimum 100ms between requests

        logger.info(f"RAWG Client initialized with base URL: {self.base_url}")

    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)

    @retry_on_failure(max_retries=config.max_retries, delay=config.retry_delay)
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request to the RAWG API.

        Args:
            endpoint (str): API endpoint
            params (dict, optional): Query parameters

        Returns:
            dict: API response data

        Raises:
            RAWGAPIError: If the API request fails
            RateLimitError: If rate limit is exceeded
        """
        self._wait_for_rate_limit()

        # Add API key to parameters
        if params is None:
            params = {}
        params['key'] = self.api_key

        url = urljoin(self.base_url, endpoint)

        try:
            logger.debug(f"Making request to: {url} with params: {params}")
            response = self.session.get(
                url, 
                params=params, 
                timeout=config.api_timeout
            )
            self.last_request_time = time.time()

            # Handle different HTTP status codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code == 404:
                return {}  # Return empty dict for not found
            else:
                response.raise_for_status()

        except requests.exceptions.Timeout:
            raise RAWGAPIError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise RAWGAPIError("Connection error")
        except requests.exceptions.RequestException as e:
            raise RAWGAPIError(f"Request failed: {str(e)}")

    @st.cache_data(ttl=config.cache_ttl, max_entries=config.max_cache_size)
    def get_games(_self, **kwargs) -> Dict[str, Any]:
        """
        Get a list of games.

        Args:
            **kwargs: Query parameters for filtering games

        Common parameters:
            search (str): Search query
            genres (str): Comma-separated genre IDs
            platforms (str): Comma-separated platform IDs
            developers (str): Comma-separated developer IDs
            publishers (str): Comma-separated publisher IDs
            tags (str): Comma-separated tag names
            dates (str): Date range (YYYY-MM-DD,YYYY-MM-DD)
            ordering (str): Ordering option
            page (int): Page number
            page_size (int): Number of results per page

        Returns:
            dict: Games data
        """
        return self._make_request(API_ENDPOINTS['games'], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_game_details(self, game_id: Union[int, str]) -> Dict[str, Any]:
        """
        Get detailed information about a specific game.

        Args:
            game_id (int|str): Game ID or slug

        Returns:
            dict: Game details
        """
        endpoint = API_ENDPOINTS['game_detail'].format(id=game_id)
        return self._make_request(endpoint)

    @st.cache_data(ttl=config.cache_ttl)
    def get_game_screenshots(self, game_id: Union[int, str]) -> Dict[str, Any]:
        """
        Get screenshots for a specific game.

        Args:
            game_id (int|str): Game ID or slug

        Returns:
            dict: Game screenshots
        """
        endpoint = API_ENDPOINTS['game_screenshots'].format(id=game_id)
        return self._make_request(endpoint)

    @st.cache_data(ttl=config.cache_ttl)
    def get_game_movies(self, game_id: Union[int, str]) -> Dict[str, Any]:
        """
        Get trailers/movies for a specific game.

        Args:
            game_id (int|str): Game ID or slug

        Returns:
            dict: Game movies/trailers
        """
        endpoint = API_ENDPOINTS['game_movies'].format(id=game_id)
        return self._make_request(endpoint)

    @st.cache_data(ttl=config.cache_ttl)
    def get_game_achievements(self, game_id: Union[int, str]) -> Dict[str, Any]:
        """
        Get achievements for a specific game.

        Args:
            game_id (int|str): Game ID or slug

        Returns:
            dict: Game achievements
        """
        endpoint = API_ENDPOINTS['game_achievements'].format(id=game_id)
        return self._make_request(endpoint)

    @st.cache_data(ttl=config.cache_ttl)
    def get_game_stores(self, game_id: Union[int, str]) -> Dict[str, Any]:
        """
        Get store links for a specific game.

        Args:
            game_id (int|str): Game ID or slug

        Returns:
            dict: Game store links
        """
        endpoint = API_ENDPOINTS['game_stores'].format(id=game_id)
        return self._make_request(endpoint)

    @st.cache_data(ttl=config.cache_ttl)
    def get_game_series(self, game_id: Union[int, str]) -> Dict[str, Any]:
        """
        Get games in the same series.

        Args:
            game_id (int|str): Game ID or slug

        Returns:
            dict: Games in series
        """
        endpoint = API_ENDPOINTS['game_series'].format(id=game_id)
        return self._make_request(endpoint)

    @st.cache_data(ttl=config.cache_ttl)
    def get_developers(self, **kwargs) -> Dict[str, Any]:
        """
        Get a list of game developers.

        Args:
            **kwargs: Query parameters

        Returns:
            dict: Developers data
        """
        return self._make_request(API_ENDPOINTS['developers'], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_developer_details(self, developer_id: Union[int, str]) -> Dict[str, Any]:
        """
        Get detailed information about a specific developer.

        Args:
            developer_id (int|str): Developer ID

        Returns:
            dict: Developer details
        """
        endpoint = API_ENDPOINTS['developer_detail'].format(id=developer_id)
        return self._make_request(endpoint)

    @st.cache_data(ttl=config.cache_ttl)
    def get_publishers(self, **kwargs) -> Dict[str, Any]:
        """
        Get a list of game publishers.

        Args:
            **kwargs: Query parameters

        Returns:
            dict: Publishers data
        """
        return self._make_request(API_ENDPOINTS['publishers'], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_publisher_details(self, publisher_id: Union[int, str]) -> Dict[str, Any]:
        """
        Get detailed information about a specific publisher.

        Args:
            publisher_id (int|str): Publisher ID

        Returns:
            dict: Publisher details
        """
        endpoint = API_ENDPOINTS['publisher_detail'].format(id=publisher_id)
        return self._make_request(endpoint)

    @st.cache_data(ttl=config.cache_ttl)
    def get_platforms(self, **kwargs) -> Dict[str, Any]:
        """
        Get a list of gaming platforms.

        Args:
            **kwargs: Query parameters

        Returns:
            dict: Platforms data
        """
        return self._make_request(API_ENDPOINTS['platforms'], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_platform_details(self, platform_id: Union[int, str]) -> Dict[str, Any]:
        """
        Get detailed information about a specific platform.

        Args:
            platform_id (int|str): Platform ID

        Returns:
            dict: Platform details
        """
        endpoint = API_ENDPOINTS['platform_detail'].format(id=platform_id)
        return self._make_request(endpoint)

    @st.cache_data(ttl=config.cache_ttl)
    def get_genres(self, **kwargs) -> Dict[str, Any]:
        """
        Get a list of game genres.

        Args:
            **kwargs: Query parameters

        Returns:
            dict: Genres data
        """
        return self._make_request(API_ENDPOINTS['genres'], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_genre_details(self, genre_id: Union[int, str]) -> Dict[str, Any]:
        """
        Get detailed information about a specific genre.

        Args:
            genre_id (int|str): Genre ID

        Returns:
            dict: Genre details
        """
        endpoint = API_ENDPOINTS['genre_detail'].format(id=genre_id)
        return self._make_request(endpoint)

    @st.cache_data(ttl=config.cache_ttl)
    def get_tags(self, **kwargs) -> Dict[str, Any]:
        """
        Get a list of game tags.

        Args:
            **kwargs: Query parameters

        Returns:
            dict: Tags data
        """
        return self._make_request(API_ENDPOINTS['tags'], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_creators(self, **kwargs) -> Dict[str, Any]:
        """
        Get a list of game creators.

        Args:
            **kwargs: Query parameters

        Returns:
            dict: Creators data
        """
        return self._make_request(API_ENDPOINTS['creators'], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_creator_details(self, creator_id: Union[int, str]) -> Dict[str, Any]:
        """
        Get detailed information about a specific creator.

        Args:
            creator_id (int|str): Creator ID

        Returns:
            dict: Creator details
        """
        endpoint = API_ENDPOINTS['creator_detail'].format(id=creator_id)
        return self._make_request(endpoint)

    @st.cache_data(ttl=config.cache_ttl)
    def get_creator_roles(self, **kwargs) -> Dict[str, Any]:
        """
        Get a list of creator roles/positions.

        Args:
            **kwargs: Query parameters

        Returns:
            dict: Creator roles data
        """
        return self._make_request(API_ENDPOINTS['creator_roles'], kwargs)

    @st.cache_data(ttl=config.cache_ttl)
    def get_stores(self, **kwargs) -> Dict[str, Any]:
        """
        Get a list of game stores.

        Args:
            **kwargs: Query parameters

        Returns:
            dict: Stores data
        """
        return self._make_request(API_ENDPOINTS['stores'], kwargs)

    def search_games(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Search for games by name.

        Args:
            query (str): Search query
            **kwargs: Additional parameters

        Returns:
            dict: Search results
        """
        params = {'search': query, **kwargs}
        return self.get_games(**params)

    def get_popular_games(self, time_period: str = "week", **kwargs) -> Dict[str, Any]:
        """
        Get popular games for a specific time period.

        Args:
            time_period (str): Time period ('week', 'month', 'year')
            **kwargs: Additional parameters

        Returns:
            dict: Popular games
        """
        # Calculate date range based on time period
        now = datetime.now()
        if time_period == "week":
            start_date = now - timedelta(weeks=1)
        elif time_period == "month":
            start_date = now - timedelta(days=30)
        elif time_period == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(weeks=1)

        dates = f"{start_date.strftime('%Y-%m-%d')},{now.strftime('%Y-%m-%d')}"
        params = {
            'dates': dates,
            'ordering': '-rating',
            **kwargs
        }
        return self.get_games(**params)

    def get_trending_games(self, **kwargs) -> Dict[str, Any]:
        """
        Get currently trending games.

        Args:
            **kwargs: Additional parameters

        Returns:
            dict: Trending games
        """
        params = {
            'ordering': '-added',
            'page_size': kwargs.get('page_size', 20),
            **kwargs
        }
        return self.get_games(**params)

    def close(self):
        """Close the HTTP session."""
        if self.session:
            self.session.close()
            logger.info("RAWG Client session closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
