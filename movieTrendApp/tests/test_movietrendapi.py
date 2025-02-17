from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from movieTrendApp.utils import integration_data

class MovieTrendAppTests(TestCase):
    """
    Test cases for the MovieTrendApp integration with Telex.
    """

    def setUp(self):
        """Set up API client for testing."""
        self.client = APIClient()
        self.telex_integration_url = reverse("movietrendapp:telex_integration")
        self.tick_url = reverse("movietrendapp:telex_tick")
        self.return_url = "https://httpbin.org/post"


    def test_get_integration_json(self):
        """Test that the integration JSON endpoint returns correct data."""
        response = self.client.get(self.telex_integration_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, integration_data)

    @patch("movieTrendApp.utils.get_top_movies")  # Mock movie fetching function
    @patch("movieTrendApp.utils.send_telex_data")   # Mock Telex data sending function
    def test_telex_tick_success(self, mock_send_telex_data, mock_get_top_movies):
        """Test tick endpoint successfully fetches and sends movie data."""

        # Mock successful movie fetch response
        mock_get_top_movies.return_value = [True, [
            {"title": "Movie 1", "vote_average": 8.5, "overview": "Movie 1 description", "poster_path": "/path1.jpg"},
            {"title": "Movie 2", "vote_average": 7.9, "overview": "Movie 2 description", "poster_path": "/path2.jpg"},
        ]]

        # Mock successful Telex data send (modify this if you changed the data structure)
        mock_send_telex_data.return_value = True

        # Simulate a Telex request with dynamic number of movies
        payload = {"return_url": self.return_url, "num_movies": 2}
        response = self.client.post(self.tick_url, data=payload, format="json")

        print(response.data)
        print(mock_get_top_movies.call_count)

        # Ensure the status code is OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"status": "success", "message": "Trending movies sent to Telex"})

        # # Assert that functions were called correctly
        # mock_get_top_movies.assert_called_once_with(2)  # Ensure it requests 2 movies

        # # Mocked function call verification (update the expected structure for send_telex_data if needed)
        # mock_send_telex_data.assert_called_once_with(
        #     url=self.return_url,
        #     movies=[{
        #         "title": "Movie 1",
        #         "rating": 8.5,
        #         "overview": "Movie 1 description",
        #         "cover_photo": "/path1.jpg"
        #     },
        #     {
        #         "title": "Movie 2",
        #         "rating": 7.9,
        #         "overview": "Movie 2 description",
        #         "cover_photo": "/path2.jpg"
        #     }]
        # )

    # @patch("movieTrendApp.utils.get_top_movies")
    # def test_telex_tick_failure(self, mock_get_top_movies):
    #     """Test tick endpoint failure when movies cannot be fetched."""



    #     payload = {"return_url": self.return_url, "num_movies": 5}
    #     response = self.client.post(self.tick_url, data=payload, format="json")

    #     # Mock a failed movie fetch response
    #     mock_get_top_movies.return_value = [False]

    #     self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    #     self.assertEqual(response.data, {"status": "error", "message": "Failed to fetch trending movies"})

    #     # Ensure the function was called with the correct number of movies
    #     mock_get_top_movies.assert_called_once_with(5)
