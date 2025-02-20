"""Utilities for my app"""

from datetime import date
import httpx
from django.conf import settings
from django.http import HttpRequest
import aiosmtplib


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
            "key_features": [
                "Fetches trending movies weekly",
                "Provides movie titles, ratings, descriptions and image url",
                "Sends movie data to Telex for processing"
            ],
            "integration_type": "interval",
            "integration_category": "Monitoring & Logging",
            "settings": [
                # {
                #     "label": "TMDb API Key",
                #     "type": "text",
                #     "required": False,
                #     "default": ""
                # },
                {
                    "label": "number-of-trending-movies",
                    "type": "number",
                    "required": False,
                    "default": 10
                },
                {
                    "label": "preferred-language",
                    "type": "dropdown",
                    "required": False,
                    "default": "en",
                    "options": ["en", "fr", "es", "de", "it", "ja", "zh"]
                },
                {
                    "label": "interval",
                    "type": "text",
                    "required": True,
                    "default": "* * * * *"  # Default to every 5 minute
                },
            ],
            "tick_url": f"{base_url}/tick",
            "target_url": ""
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
    num_movies = int(telex_data.get("number-of-trending-movies", 10))
    preferred_language = telex_data.get("preferred-language", "en")
    # Get number of movies to fetch

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
            message += f"\n{i}. {movie['title']} - {movie.get('rating', 'N/A')}\n"
            message += f"Overview: {movie['overview']}\n"
            message += f"Image URL: {movie.get('cover_photo', 'N/A')}\n\n"

        # Payload for Telex
        data = {
            "message": message,
            "username": "Movie Trend",
            "event_name": "Trending Movies Fetch",
            "status": "success"
        }

        # Send POST request to Telex API
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)

        # Send Email Notification using aiosmtplib
        await send_email_notification()

        return response.status_code >= 200

    except httpx.HTTPError as http_error:
        print(f"Error sending data to Telex: {http_error}")
        return False


async def send_email_notification():
    """
    Asynchronously sends an email notification using aiosmtplib.
    """
    message = (
        "Subject: Telex Notification\n\n"
        "Telex called your tick endpoint successfully."
    )

    try:
        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=465,
            username=settings.HOST_USER,
            password=settings.HOST_PASSWORD,
            use_tls=True,
            sender=settings.HOST_USER,
            recipients=[settings.HOST_USER],
        )
    except aiosmtplib.SMTPException as email_error:
        print(f"Email sending failed: {email_error}")