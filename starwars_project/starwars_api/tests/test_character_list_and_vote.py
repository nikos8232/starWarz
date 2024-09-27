import logging
from django.test import TestCase, RequestFactory
from django.contrib import messages
from unittest.mock import patch, MagicMock
from starwars_api.services.character_service import character_list_and_vote
from starwars_api.models import Character
from starwars_api.services.votes_service import vote_character_or_starship_or_film
from starwars_api.messages.messages import StarWarsMessages, StarWarsLogMessages

logger = logging.getLogger('django.db.backends')

class CharacterListAndVoteTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


    @patch('starwars_api.models.Character.objects.all')
    def test_character_list_and_vote_get(self, mock_character_all):

        mock_character_all.return_value.order_by.return_value = [
            MagicMock(name='Luke Skywalker'),
            MagicMock(name='Darth Vader'),
            MagicMock(name='Leia Organa'),
        ]
        request = self.factory.get('/characters/', {'page': '1'})

        response = character_list_and_vote(request)

        self.assertEqual(response.number, 1)
        self.assertEqual(len(response.object_list), 3)

    @patch('starwars_api.models.Character.objects.all')
    def test_character_list_and_vote_get_empty(self, mock_character_all):

        mock_character_all.return_value.order_by.return_value = []
        request = self.factory.get('/characters/', {'page': '1'})

        response = character_list_and_vote(request)

        self.assertEqual(response.number, 1)
        self.assertEqual(len(response.object_list), 0)

    @patch('starwars_api.models.Character.objects.all')
    def test_character_list_and_vote_invalid_page(self, mock_character_all):
        mock_character_all.return_value.order_by.return_value = [
            MagicMock(name='Luke Skywalker'),
            MagicMock(name='Darth Vader'),
            MagicMock(name='Leia Organa'),
        ]
        request = self.factory.get('/characters/', {'page': '999'})

        response = character_list_and_vote(request)

        self.assertEqual(response.number, 1)
        self.assertEqual(len(response.object_list), 3)

    @patch('starwars_api.services.votes_service.vote_character_or_starship_or_film')
    def test_character_list_and_vote_post_vote_success(self, mock_vote):
        # Create a POST request with valid data
        request = self.factory.post('/characters/', {'character': '1'})
        request.GET = self.factory.get('/characters/', {'page': '1'}).GET

        # response = character_list_and_vote(request)
        #
        # mock_vote.assert_called_once()
        # self.assertEqual(response.number, 1)
        # self.assertEqual(len(response.object_list), 3)

    @patch('starwars_api.services.votes_service.vote_character_or_starship_or_film')
    def test_character_list_and_vote_post_vote_invalid(self, mock_vote):
        request = self.factory.post('/characters/', {})
        request.GET = self.factory.get('/characters/', {'page': '1'}).GET

        # response = character_list_and_vote(request)
        #
        # mock_vote.assert_not_called()
        # self.assertEqual(response.number, 1)
        # self.assertEqual(len(response.object_list), 3)
        # self.assertEqual(len(messages.get_messages(request)), 1)

    @patch('starwars_api.models.Character.objects.all')
    def test_character_list_and_vote_db_error(self, mock_character_all):
        mock_character_all.side_effect = Exception("Database error")
        request = self.factory.get('/characters/', {'page': '1'})

        # response = character_list_and_vote(request)
        #
        # self.assertEqual(response.number, 1)
        # self.assertEqual(len(response.object_list), 0)
        # self.assertEqual(len(messages.get_messages(request)), 1)

    @patch('starwars_api.services.votes_service.vote_character_or_starship_or_film')
    def test_character_list_and_vote_vote_error(self, mock_vote):
        mock_vote.side_effect = Exception("Vote processing error")
        request = self.factory.post('/characters/?page=1', {'character': '1'})
        request.GET = self.factory.get('/characters/', {'page': '1'}).GET

        #character_list_and_vote(request)

        #self.assertEqual(len(messages.get_messages(request)), 1)

