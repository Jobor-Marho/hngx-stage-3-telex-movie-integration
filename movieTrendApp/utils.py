"""Utilities for my app"""

from datetime import date
import httpx
from django.conf import settings
from django.http import HttpRequest


def get_base_url(request: HttpRequest):
    """
    Dynamically get the base URL of the running application.
    """
    scheme = "https" if request.is_secure() else "http"
    return f"{scheme}://{request.get_host()}"

def get_integration_data(request: HttpRequest):
    """
    Generate integration data dynamically with the correct domain.
    """
    base_url = get_base_url(request)

    return {
        "data": {
            "date": {
                "created_at": str(date.today()),
                "updated_at": str(date.today())
            },
            "descriptions": {
                "app_description": "Fetches and provides trending movies from the past week.",
                "app_logo": f"{base_url}{settings.STATIC_URL}logo/logo.jpeg",
                "app_name": "MovieTrend",
                "app_url": f"{base_url}",
                "background_color": "#000000"
            },
            "author": "Edric Oghenejobor",
            "integration_type": "interval",
            "key_features": [
                "Fetches trending movies weekly",
                "Provides movie titles, ratings, descriptions and image url",
                "Sends movie data to Telex for processing"
            ],
            "settings": [
                {
                    "label": "Interval",
                    "type": "text",
                    "description": "Crontab format for scheduling the fetch operation.",
                    "required": True,
                    "default": "* * * * *"  # Default to every minute
                },
                {
                    "label": "TMDb API Key",
                    "type": "text",
                    "description": "API key for accessing TMDb movie data.",
                    "required": False,
                    "default": ""
                },
                {
                    "label": "Number of Trending Movies",
                    "type": "number",
                    "description": "How many trending movies to fetch (e.g., 5, 10, 20).",
                    "required": False,
                    "default": 10
                },
                {
                    "label": "Preferred Language",
                    "type": "dropdown",
                    "description": "Select the language for movie titles and descriptions.",
                    "required": False,
                    "default": "en",
                    "options": ["en", "fr", "es", "de", "it", "ja", "zh"]
                }
            ],
            "tick_url": f"{base_url}/tick/",
            "target_url": None
        }
    }



async def generate_img_url(poster_path: str) -> str:
    """
    Asynchronously generates a complete image URL for the given poster path.

    Args:
        poster_path (str): Poster path for the movie.

    Returns:
        str: URL for the image or an error message.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.CONFIG_URL, headers=settings.HEADERS)
            response.raise_for_status()
            config_data = response.json()

        base_url = config_data.get("images", {}).get("base_url", "")
        poster_sizes = config_data.get("images", {}).get("poster_sizes", [])
        size = poster_sizes[4] if len(poster_sizes) > 4 else poster_sizes[0] if poster_sizes else ""

        if base_url and size and poster_path:
            return f"{base_url}{size}{poster_path}"
        return "Invalid URL configuration."
    except httpx.HTTPError as e:
        return {"error": f"Error generating image URL: {str(e)}"}


async def get_top_movies(telex_data):
    """
    Asynchronously fetch trending movies with a customizable limit.

    Args:
        telex_data (dict): Data received from Telex, including preferences and API details.

    Returns:
        list: [Success (bool), List of movies, Return URL]
    """

    return_url = telex_data.get("return_url")  # Telex sends this URL for posting results
    api_key = telex_data.get("api_key")  # API key provided by Telex
    preferred_language = telex_data.get("preferred_language", "en")  # Default to English
    num_movies = int(telex_data.get("num_movies", 10))  # Get number of movies to fetch

    headers = {
        "Content-Type": f"{settings.CONTENT_TYPE}"
    }

    if api_key:
        # Use API key if provided
        url = f"{settings.MDBURL}api_key={api_key}&language={preferred_language}"
    else:
        # Default to using Bearer token
        url = f"{settings.MDBURL}language={preferred_language}"
        headers["Authorization"] = f"Bearer {settings.BEARER_KEY}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            movies = response.json().get("results", [])

        return [True, movies[:num_movies], return_url]  # Return only the requested number of movies

    except httpx.HTTPError:
        return [False, [], return_url]


async def send_telex_data(url: str, movies: list):
    """
    Asynchronously sends trending movie data to Telex.

    Args:
        url (str): Telex API endpoint.
        movies (list): List of movie data.

    Returns:
        bool: True if successfully sent, False otherwise.
    """
    try:
        # Prepare the message for Telex
        message = f"🎬🍿 Top {len(movies)} Trending Movies for the Week 🎬🍿:\n"
        for i, movie in enumerate(movies, start=1):
            message += f"\n{i}. {movie['title']} - {movie.get('rating', 'N/A')}\n\n"
            message += f"Overview: {movie['overview']}\n\n"
            message += f"Image Url: {movie['cover_photo']}\n\n\n"

        # Build the payload in the correct format for Telex
        data = {
            "message": message,
            "username": "Movie Trend",
            "event_name": "Trending Movies Fetch",
            "status": "success"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)

        return response.status_code >= 200

    except httpx.HTTPError as e:
        print(f"Error sending data to Telex: {e}")
        return False
