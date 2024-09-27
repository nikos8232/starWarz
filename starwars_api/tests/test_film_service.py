from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
from starwars_api.models import Film
from starwars_api.services.film_service import list_film_and_vote


class ListFilmAndVoteTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/films/')


    @patch('starwars_api.models.Film.objects.all')
    @patch('django.core.paginator.Paginator.get_page')
    @patch('starwars_api.services.votes_service.vote_character_or_starship_or_film')
    def test_list_films_successful(self, mock_vote, mock_get_page, mock_film_objects):
        mock_film_objects.return_value.order_by.return_value = [
            Film(title='A New Hope', episode_id=4),
            Film(title='The Empire Strikes Back', episode_id=5)
        ]

        mock_get_page.return_value = ['A New Hope', 'The Empire Strikes Back']

        response = list_film_and_vote(self.request)

        mock_film_objects.assert_called_once()
        mock_get_page.assert_called_once_with(None)
        self.assertEqual(len(response), 2)

    @patch('starwars_api.models.Film.objects.all')
    @patch('django.core.paginator.Paginator.get_page')
    @patch('starwars_api.services.votes_service.vote_character_or_starship_or_film')
    @patch('starwars_api.services.film_service.messages')
    def test_database_error_handling(self, mock_messages, mock_vote, mock_get_page, mock_film_objects):
        mock_film_objects.side_effect = Exception("Database error")
        mock_messages.error = MagicMock()
        response = list_film_and_vote(self.request)
        # WIP

    @patch('starwars_api.models.Film.objects.all')
    @patch('django.core.paginator.Paginator.get_page')
    @patch('starwars_api.services.film_service.vote_character_or_starship_or_film')
    @patch('starwars_api.services.film_service.messages')
    def test_vote_handling(self, mock_messages, mock_vote, mock_get_page, mock_film_objects):
        mock_film_objects.return_value.order_by.return_value = [
            Film(title='A New Hope', episode_id=4),
            Film(title='The Empire Strikes Back', episode_id=5)
        ]

        mock_get_page.return_value = ['A New Hope', 'The Empire Strikes Back']

        self.request.method = 'POST'
        self.request.POST = {'film': 'A New Hope'}
        mock_messages.error = MagicMock()

        list_film_and_vote(self.request)

        self.assertEqual(mock_vote.call_count, 1)

    @patch('starwars_api.models.Film.objects.all')
    @patch('django.core.paginator.Paginator.get_page')
    @patch('starwars_api.services.votes_service.vote_character_or_starship_or_film')
    @patch('starwars_api.services.film_service.messages')
    def test_invalid_vote_handling(self, mock_messages, mock_vote, mock_get_page, mock_film_objects):
        mock_film_objects.return_value.order_by.return_value = [
            Film(title='A New Hope', episode_id=4),
            Film(title='The Empire Strikes Back', episode_id=5)
        ]

        mock_get_page.return_value = ['A New Hope', 'The Empire Strikes Back']

        self.request.method = 'POST'
        self.request.POST = {}
        mock_messages.error = MagicMock()
        list_film_and_vote(self.request)

        mock_vote.assert_not_called()

