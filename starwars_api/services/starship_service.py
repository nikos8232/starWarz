import logging

from django.contrib import messages
from django.core.paginator import Paginator

from starwars_api.models import Starship, Vote
from starwars_api.services.votes_service import vote_character_or_starship_or_film
from starwars_api.messages.messages import StarWarsMessages, StarWarsLogMessages

logger = logging.getLogger('django.db.backends')


def starship_list_and_vote(request):

    starships = []
    try:
        starships = Starship.objects.all().order_by('name')
    except Exception as e:
        logger.error(StarWarsLogMessages.DATABASE_ERROR_STARSHIP + str(e))
        messages.error(request, StarWarsMessages.DATABASE_ERROR_STARSHIP)

    paginator = Paginator(starships, 4)
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