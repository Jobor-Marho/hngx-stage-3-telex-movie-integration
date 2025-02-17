"""View for Accessing Integration Json and Tick Endoipoint"""
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .utils import (integration_data, generate_img_url, get_top_movies, send_telex_data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_integration_json(request):
    """Return the integration JSON used by telex"""
    return Response(data=integration_data, status=status.HTTP_200_OK, content_type="application/json")



@api_view(["POST"])
@permission_classes([AllowAny])
def telex_tick(request):
    """
    Handles tick_url requests from Telex. Fetches trending movies and sends them to Telex.
    """
    telex_data = request.data
    return_url = telex_data.get("return_url")  # Telex sends this URL for posting results

    # Get the number of movies to fetch (default to 10)
    num_movies = int(telex_data.get("num_movies", 10))

    # Fetch the top movies and handle any errors
    success, movies = get_top_movies(num_movies)

    if success:
        # Extract relevant movie details
        trending_movies = [
            {
                "title": movie["title"],
                "rating": movie["vote_average"],
                "overview": movie["overview"],
                "cover_photo": generate_img_url(movie["poster_path"])
            }
            for movie in movies
        ]

        # Send data back to Telex using return_url
        send_success = send_telex_data(url=return_url, movies=trending_movies)
        if send_success:
            return Response(data={"status": "success", "message": "Trending movies sent to Telex"}, status=status.HTTP_200_OK)

        return Response(data={"status": "error", "message": "Failed to send movie data to Telex"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(data={"status": "error", "message": "Failed to fetch trending movies"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
