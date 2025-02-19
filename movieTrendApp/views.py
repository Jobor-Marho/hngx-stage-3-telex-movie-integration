"""View for Accessing Integration Json and Tick Endoipoint"""
from rest_framework import status
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .utils import (get_integration_data, generate_img_url, get_top_movies, send_telex_data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_integration_json(request) -> JsonResponse:
    """Return the integration JSON to be used by telex"""
    return JsonResponse(data=get_integration_data(request), status=status.HTTP_200_OK)




@api_view(["POST"])
@permission_classes([AllowAny])
def telex_tick(request):
    """
    Handles tick_url requests from Telex. Fetches trending movies and sends them to Telex.
    """
    telex_data = request.data



    # Fetch the top movies using the extracted API key and language
    success, movies, url = get_top_movies(telex_data)
    

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
        send_success = send_telex_data(url, movies=trending_movies)
        if send_success:
            return Response(data={"status": "success", "message": "Trending movies sent to Telex"}, status=status.HTTP_200_OK)

        return Response(data={"status": "error", "message": "Failed to send movie data to Telex"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(data={"status": "error", "message": "Failed to fetch trending movies"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)