from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
from starwars_api.models import Starship
from starwars_api.services.starship_service import starship_list_and_vote
from starwars_api.messages.messages import StarWarsMessages


class StarshipListAndVoteTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/starships/')


    @patch('starwars_api.models.Starship.objects.all')
    @patch('django.core.paginator.Paginator.get_page')
    @patch('starwars_api.services.votes_service.vote_character_or_starship_or_film')
    def test_starship_list_successful(self, mock_vote, mock_get_page, mock_starship_objects):
        mock_starship_objects.return_value.order_by.return_value = [
            Starship(name='X-wing', model='T-65 X-wing starfighter'),
            Starship(name='TIE Fighter', model='TIE/ln space superiority starfighter')
        ]

        mock_get_page.return_value = ['X-wing', 'TIE Fighter']

        response = starship_list_and_vote(self.request)

        mock_starship_objects.assert_called_once()
        mock_get_page.assert_called_once_with(None)
        self.assertEqual(len(response), 2)

    @patch('starwars_api.models.Starship.objects.all')
    @patch('django.core.paginator.Paginator.get_page')
    @patch('starwars_api.services.votes_service.vote_character_or_starship_or_film')
    @patch('starwars_api.services.starship_service.messages')
    def test_database_error_handling(self, mock_messages, mock_vote, mock_get_page, mock_starship_objects):
        mock_starship_objects.side_effect = Exception("Database error")

        response = starship_list_and_vote(self.request)

        # WIP

    @patch('starwars_api.models.Starship.objects.all')
    @patch('django.core.paginator.Paginator.get_page')
    @patch('starwars_api.services.starship_service.vote_character_or_starship_or_film')
    @patch('starwars_api.services.starship_service.messages')
    def test_vote_handling(self, mock_messages, mock_vote, mock_get_page, mock_starship_objects):
        mock_starship_objects.return_value.order_by.return_value = [
            Starship(name='X-wing', model='T-65 X-wing starfighter'),
            Starship(name='TIE Fighter', model='TIE/ln space superiority starfighter')
        ]

        mock_get_page.return_value = ['X-wing', 'TIE Fighter']

        self.request.method = 'POST'
        self.request.POST = {'starship': 'X-wing'}
        mock_messages.error = MagicMock()

        starship_list_and_vote(self.request)
        self.assertEqual(mock_vote.call_count, 1)


    @patch('starwars_api.models.Starship.objects.all')
    @patch('django.core.paginator.Paginator.get_page')
    @patch('starwars_api.services.votes_service.vote_character_or_starship_or_film')
    @patch('starwars_api.services.starship_service.messages')
    def test_invalid_vote_handling(self, mock_messages, mock_vote, mock_get_page, mock_starship_objects):
        mock_starship_objects.return_value.order_by.return_value = [
            Starship(name='X-wing', model='T-65 X-wing starfighter'),
            Starship(name='TIE Fighter', model='TIE/ln space superiority starfighter')
        ]

        mock_get_page.return_value = ['X-wing', 'TIE Fighter']


        self.request.method = 'POST'
        self.request.POST = {}

        starship_list_and_vote(self.request)
        mock_vote.assert_not_called()

