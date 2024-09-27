import logging

from django.contrib import messages
from django.core.paginator import Paginator

from starwars_api.models import Character, Vote
from starwars_api.services.votes_service import vote_character_or_starship_or_film
from starwars_api.messages.messages import StarWarsMessages, StarWarsLogMessages

logger = logging.getLogger('django.db.backends')


def character_list_and_vote(request):
    """
    Retrieve a paginated list of characters and handle voting logic.

    This function retrieves all characters from the database and orders them alphabetically.
    It also supports pagination and handles POST requests for voting on characters, films, or starships.

    Args:
        request (HttpRequest): The HTTP request object, containing GET or POST data.

    Returns:
        Paginator.page: A paginated list of characters for the current page.

    GET:
        Retrieves the list of characters and paginates them.

    POST:
        Processes a vote for a character, film, or starship and handles any errors or invalid votes.

    Errors Handled:
        - Database retrieval errors (Character list)
        - Pagination errors (Invalid page number)
        - Invalid or missing vote data in POST request
        - Errors during vote processing
    """
    characters = []
    try:
        characters = Character.objects.all().order_by('name')
    except Exception as e:
        logger.error(StarWarsLogMessages.DATABASE_ERROR + str(e))
        messages.error(request, StarWarsMessages.DATABASE_ERROR_CHARACTER)

    paginator = Paginator(characters, 4)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except Exception as e:
        logger.error(StarWarsLogMessages.PAGINATOR_ERROR + str(e))
        page_obj = paginator.get_page(1)

    if request.method == 'POST':
        try:
            if not request.POST.get('character') and not request.POST.get('film') and not request.POST.get('starship'):
                messages.error(request, StarWarsMessages.INVALID_VOTE_REQUEST)
                return page_obj
            vote_character_or_starship_or_film(request)
        except Exception as e:
            logger.error(StarWarsLogMessages.ERROR_DURING_VOTING + str(e))
            messages.error(request, StarWarsMessages.ERROR_DURING_VOTE)
    return page_obj



