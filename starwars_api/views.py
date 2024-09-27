import logging

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view

from starwars_api.models import Character, Film, Starship, Vote
from starwars_api.services import fetch_and_store_data, votes_service, character_service, starship_service, film_service

from starwars_api.messages.messages import StarWarsMessages

logger = logging.getLogger('django.db.backends')

@api_view(['GET', 'POST'])
def populate_db(request):
    """
    View to trigger the population of the database with Star Wars data.

    Fetches data from an external API and stores it in the database using the `fetch_and_store_data` service.
    Returns a JSON response with a success message if successful, or an error message if an exception occurs.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.
    """
    try:
        fetch_and_store_data.fetch_and_store_data()
        return JsonResponse({"status": "success", "message": "Database populated!"})
    except Exception as e:
        return HttpResponseBadRequest(StarWarsMessages.ERROR_POPULATING_DATABASE + str(e))

@api_view(['GET', 'POST'])
def list_items(request, item_type):
    """
    View to list characters, starships, or films, along with their vote data.

    Args:
        request (HttpRequest): The HTTP request object.
        item_type (str): The type of item to list ('character', 'starship', or 'film').

    Returns:
        HttpResponse: Renders the corresponding HTML template for the requested item type,
        or a JSON response with an error if the item type is invalid.
    """
    service_map = {
        'character': character_service.character_list_and_vote,
        'starship': starship_service.starship_list_and_vote,
        'film': film_service.list_film_and_vote
    }

    if item_type not in service_map:
        logger.error(f"Invalid item type.: {str(item_type)}")
        return JsonResponse({"status": "error", "message": StarWarsMessages.INVALID_ITEM_TYPE}, status=400)

    page_obj = service_map[item_type](request)

    return render(request, f'{item_type}_list.html', {'page_obj': page_obj})

@api_view(['GET'])
def search_page(request):
    """
    View to search for characters, films, or starships by name or title.

    Processes the search query passed via GET parameters and filters results from Character, Film, and Starship models.
    Displays the search results on the search_page.html template.

    Args:
        request (HttpRequest): The HTTP request object containing the search query.

    Returns:
        HttpResponse: Renders the search results on the 'search_page.html' template.
    """
    query = request.GET.get('query', '')
    results = {"characters": [], "films": [], "starships": []}

    if query:
        results["characters"] = Character.objects.filter(name__icontains=query)
        results["films"] = Film.objects.filter(title__icontains=query)
        results["starships"] = Starship.objects.filter(name__icontains=query)

    return render(request, 'search_page.html', {'results': results})


@api_view(['POST'])
def post_vote(request):
    """
    View to handle the submission of a vote for a character, film, or starship.

    Delegates the vote creation logic to the `votes_service`. If successful, renders a vote confirmation page.
    In case of an error during vote processing, logs the error and returns a bad request response.

    Args:
        request (HttpRequest): The HTTP request object containing vote data.

    Returns:
        HttpResponse: Renders the 'vote.html' template with characters, films, and starships,
        or returns a bad request if an error occurs.
    """
    try:
        votes_service.vote_create(request)
    except Exception as e:
        logger.error(f"Error processing vote: {str(e)}")
        return HttpResponseBadRequest(StarWarsMessages.ERROR_PROCESSING_VOTE + str(e))

    characters = Character.objects.all()
    films = Film.objects.all()
    starships = Starship.objects.all()
    context = {'characters': characters, 'films': films, 'starships': starships}

    return render(request, 'vote.html', context)


@api_view(['GET'])
def vote_list_view(request):
    """
   View to display a list of all recorded votes.

   Retrieves all votes from the database, along with related character, film, and starship data,
   and renders them on the 'vote_list.html' template.

   Args:
       request (HttpRequest): The HTTP request object.

   Returns:
       HttpResponse: Renders the 'vote_list.html' template with the list of votes.
   """
    votes = Vote.objects.select_related('character', 'film', 'starship')

    return render(request, 'vote_list.html', {'votes': votes})