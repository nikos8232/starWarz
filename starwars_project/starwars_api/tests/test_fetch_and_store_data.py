
from unittest import TestCase
from unittest.mock import patch, MagicMock
from starwars_api.services.fetch_and_store_data import fetch_and_store_data, fetch_films, fetch_characters, fetch_starships  # Adjust the import according to your app structure

class FetchDataTests(TestCase):

    @patch('starwars_api.services.fetch_and_store_data.requests.get')
    @patch('starwars_api.models.Film.objects.update_or_create')
    def test_fetch_films(self, mock_film_objects, mock_requests_get):
        mock_response = {
            "results": [
                {
                    "title": "A New Hope",
                    "episode_id": 4,
                    "url": "https://swapi.dev/api/films/1/",
                    "release_date": "1977-05-25"
                },
                {
                    "title": "The Empire Strikes Back",
                    "episode_id": 5,
                    "url": "https://swapi.dev/api/films/2/",
                    "release_date": "1980-05-21"
                }
            ]
        }
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = mock_response

        fetch_films()

        self.assertEqual(mock_film_objects.call_count, 2)

    @patch('starwars_api.services.fetch_and_store_data.requests.get')
    @patch('starwars_api.models.Character.objects.update_or_create', return_value=(MagicMock(films=MagicMock()), MagicMock()))
    @patch('starwars_api.services.fetch_and_store_data.Film.objects.get')
    @patch('starwars_api.models.Character.save')
    def test_fetch_characters(self, mock_save, mock_film_get, mock_character_objects, mock_requests_get):
        mock_response = {
            "results": [
                {
                    "name": "Luke Skywalker",
                    "height": "172",
                    "mass": "77",
                    "films": ["https://swapi.dev/api/films/1/"]
                }
            ]
        }
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = mock_response
        mock_film_get.return_value = MagicMock(name='Luke Skywalker')
        mock_character_objects[0].films.add = MagicMock()

        fetch_characters()

        mock_character_objects.assert_called_once_with(
            name='Luke Skywalker',
            height='172',
            mass='77'
        )


    @patch('starwars_api.services.fetch_and_store_data.requests.get')
    @patch('starwars_api.models.Starship.objects.update_or_create', return_value=(MagicMock(films=MagicMock()), MagicMock()))
    @patch('starwars_api.models.Film.objects.get')
    def test_fetch_starships(self, mock_film_get, mock_starship_objects, mock_requests_get):
        # Mock the response from the SWAPI
        mock_response = {
            "results": [
                {
                    "name": "Millennium Falcon",
                    "model": "YT-1300 light freighter",
                    "manufacturer": "Corellian Engineering Corporation",
                    "length": "34.37",
                    "crew": "4",
                    "passengers": "6",
                    "films": ["https://swapi.dev/api/films/1/"]
                }
            ]
        }
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = mock_response
        mock_film_get.return_value = MagicMock(name='Film 1')
        mock_starship_objects[0].films.add = MagicMock()

        fetch_starships()

        mock_starship_objects.assert_called_once_with(
            name='Millennium Falcon',
            model='YT-1300 light freighter',
            manufacturer='Corellian Engineering Corporation',
            length='34.37',
            crew=4,
            passengers='6'
        )
