"""Utilities for my app"""

from datetime import date
import requests
from django.conf import settings





integration_data = {
    "data": {
        "date": {
            "created_at": str(date.today()),
            "updated_at": str(date.today())
        },
        "descriptions": {
            "app_description": "Fetches and provides trending movies from the past week.",
            "app_logo": f"{settings.BASE_URL}{settings.STATIC_URL}logo/logo.jpeg",
            "app_name": "MovieTrend",
            "app_url": f"{settings.BASE_URL}",
            "background_color": "#000000"
        },
        "integration_category": "Monitoring & Logging",
        "author": "Edric Oghenejobor",
        "integration_type": "interval",
        "is_active": True,
        "output": [
            {
                "label": "Trending Movies",
                "value": True
            }
        ],
        "key_features": [
            "Fetches trending movies weekly",
            "Provides movie titles, ratings, and descriptions",
            "Sends movie data to Telex for processing"
        ],
        "permissions": {
            "monitoring_user": {
                "always_online": True,
                "display_name": "Movie Tracker"
            }
        },
        "settings": [
            {
                "label": "Interval",
                "type": "text",
                "description": "Crontab format for scheduling the fetch operation.",
                "required": True,
                "default": "0 0 * * 0"  # Runs every Sunday at midnight
            },
            {
                "label": "TMDb API Key",
                "type": "text",
                "description": "API key for accessing TMDb movie data.",
                "required": True,
                "default": ""
            },
            {
                "label": "Number of Trending Movies",
                "type": "number",
                "description": "How many trending movies to fetch (e.g., 5, 10, 20).",
                "required": True,
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
        "tick_url": f"{settings.BASE_URL}/tick/",
    }
}

def generate_img_url(poster_path: str) -> str:
    """
    Generates a complete image URL for the given poster path.

    Args:
        poster_path (str): Poster path for the movie.

    Returns:
        str: URL for the image or an error message.
    """
    try:
        response = requests.get(settings.CONFIG_URL, headers=settings.HEADERS)
        response.raise_for_status()
        config_data = response.json()
        base_url = config_data.get("images", {}).get("base_url", "")
        poster_sizes = config_data.get("images", {}).get("poster_sizes", [])
        size = poster_sizes[4] if len(poster_sizes) > 4 else poster_sizes[0] if poster_sizes else ""
        if base_url and size and poster_path:
            return f"{base_url}{size}{poster_path}"
        return "Invalid URL configuration."
    except requests.exceptions.RequestException as e:
        return {"error": f"Error generating image URL: {str(e)}"}

def get_top_movies(limit: int = 10):
    """
    Fetch trending movies with a customizable limit.

    Args:
        limit (int): Number of movies to fetch (default is 10).

    Returns:
        list: [Success (bool), List of movies]
    """
    response = requests.get(settings.MDBURL, headers=settings.HEADERS)

    if response.status_code == 200:
        movies = response.json().get("results", [])
        return [True, movies[:limit]]  # Return only the requested number of movies

    return [False]


def send_telex_data(url: str, movies: list):
    try:
        # Prepare the message for Telex (customize as needed)
        message = f"Trending Movies:\n" + "\n".join([f"{movie['title']} - {movie['rating']}" for movie in movies])

        # Build the payload in the correct format for Telex
        data = {
            "message": message,
            "username": "Movie Trend",
            "event_name": "Trending Movies Fetch",
            "status": "success"  # Or "error" based on the outcome
        }

        # Make the POST request with the correct format
        response = requests.post(url, json=data)


        # Check if the request was successful
        if response.status_code == 200:
            return True  # Successfully sent data
        else:
            # Log error or raise exception
            return False
    except requests.exceptions.RequestException as e:
        # Log the error (or re-raise)
        print(f"Error sending data to Telex: {e}")
        return False
