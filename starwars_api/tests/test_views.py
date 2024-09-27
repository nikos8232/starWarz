import json
from django.test import TestCase, RequestFactory
from django.urls import reverse
from unittest.mock import patch, MagicMock
from starwars_api.views import populate_db, list_items, search_page, post_vote, vote_list_view
from starwars_api.messages.messages import StarWarsMessages
from starwars_api.models import Character, Film, Starship, Vote


class StarWarsApiTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('starwars_api.services.fetch_and_store_data.fetch_and_store_data')
    def test_populate_db_success(self, mock_fetch_and_store_data):
        request = self.factory.post(reverse('populate'))
        response = populate_db(request)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success", "message": "Database populated!"})
        mock_fetch_and_store_data.assert_called_once()

    @patch('starwars_api.services.fetch_and_store_data.fetch_and_store_data')
    def test_populate_db_failure(self, mock_fetch_and_store_data):
        mock_fetch_and_store_data.side_effect = Exception("Fetch error")
        request = self.factory.post(reverse('populate'))
        response = populate_db(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn(StarWarsMessages.ERROR_POPULATING_DATABASE, str(response.content))

    @patch('starwars_api.services.character_service.character_list_and_vote')
    @patch('starwars_api.services.starship_service.starship_list_and_vote')
    @patch('starwars_api.services.film_service.list_film_and_vote')
    def test_list_items_valid(self, mock_list_film, mock_list_starship, mock_list_character):
        item_type = 'character'
        mock_list_character.return_value = MagicMock()  # Mocked return value
        request = self.factory.get(reverse('list-items', args=[item_type]))

        response = list_items(request, item_type)

        self.assertEqual(response.status_code, 200)
        mock_list_character.assert_called_once()

    def test_list_items_invalid(self):
        item_type = 'invalid'
        request = self.factory.get(reverse('list-items', args=[item_type]))

        response = list_items(request, item_type)

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"status": "error", "message": StarWarsMessages.INVALID_ITEM_TYPE})

    @patch('starwars_api.models.Character')
    @patch('starwars_api.models.Film')
    @patch('starwars_api.models.Starship')
    def test_search_page(self, mock_starship, mock_film, mock_character):
        query = 'test'
        request = self.factory.get(reverse('search-page'), {'query': query})

        mock_character.objects.filter.return_value = ['character1']
        mock_film.objects.filter.return_value = ['film1']
        mock_starship.objects.filter.return_value = ['starship1']

        response = search_page(request)

        self.assertEqual(response.status_code, 200)


    @patch('starwars_api.services.votes_service.vote_create')
    @patch('starwars_api.models.Character.objects.all')
    @patch('starwars_api.models.Film.objects.all')
    @patch('starwars_api.models.Starship.objects.all')
    def test_post_vote_success(self, mock_starship, mock_film, mock_character, mock_vote_create):
        request = self.factory.post(reverse('vote-create'), {'vote_data': 'data'})
        mock_vote_create.return_value = None
        mock_character.return_value = ['character1']
        mock_film.return_value = ['film1']
        mock_starship.return_value = ['starship1']

        response = post_vote(request)

        self.assertEqual(response.status_code, 200)
        mock_vote_create.assert_called_once()

    @patch('starwars_api.services.votes_service.vote_create')
    def test_post_vote_failure(self, mock_vote_create):
        mock_vote_create.side_effect = Exception("Vote error")
        request = self.factory.post(reverse('vote-create'), {'vote_data': 'data'})

        response = post_vote(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn(StarWarsMessages.ERROR_PROCESSING_VOTE, str(response.content))

    @patch('starwars_api.models.Vote.objects.select_related')
    def test_vote_list_view(self, mock_select_related):
        mock_votes = MagicMock()
        mock_select_related.return_value = mock_votes
        request = self.factory.get(reverse('vote-list'))

        response = vote_list_view(request)

        self.assertEqual(response.status_code, 200)
        mock_select_related.assert_called_once_with('character', 'film', 'starship')
