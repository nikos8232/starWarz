import logging

from django.contrib import messages
from django.db import IntegrityError, transaction

from starwars_api.models import Vote, Character, Film, Starship
from starwars_api.messages.messages import StarWarsMessages, StarWarsLogMessages

logger = logging.getLogger('django.db.backends')


def vote_create(request):

    try:
        with transaction.atomic():
            if request.method == 'POST':
                character_id = request.POST.get('character')
                film_id = request.POST.get('film')
                starship_id = request.POST.get('starship')
                voter_ip = request.META.get('REMOTE_ADDR')

                if not character_id and not film_id and not starship_id:
                    message = StarWarsMessages.REQUIRED_FIELDS
                    logger.error(f"Validate input: {message}")
                    return messages.error(request, message)

                try:
                    vote = Vote.objects.create(
                        character_id=character_id if character_id else None,
                        film_id=film_id if film_id else None,
                        starship_id=starship_id if starship_id else None,
                        voter_ip=voter_ip
                    )
                    return messages.success(request, StarWarsMessages.SUCCESSFULLY_VOTE)

                except IntegrityError as e:
                    logger.error(f"Database Error: {e}")
                    return messages.error(request, StarWarsMessages.ALREADY_VOTED)

    except Exception as e:
        logger.error(f"Error: {e}")
        return messages.error(request, StarWarsMessages.SOMETHING_WENT_WRONG)


def vote_character_or_starship_or_film(request):

    try:
        with transaction.atomic():
            character_id = request.POST.get('character')
            film_id = request.POST.get('film')
            starship_id = request.POST.get('starship')
            voter_ip = request.META.get('REMOTE_ADDR')

            character = None
            film = None
            starship = None
            if character_id:
                character = Character.objects.get(id=character_id)
            elif film_id:
                film = Film.objects.get(id=film_id)
            elif starship_id:
                starship = Starship.objects.get(id=starship_id)

            if Vote.objects.filter(character=character, voter_ip=voter_ip, film=film, starship=starship).exists():
                return messages.error(request, StarWarsMessages.ALREADY_VOTED)
            else:
                vote_create(request)

    except Exception as e:
        logger.error(f"Error: {e}")
        return messages.error(request, StarWarsMessages.SOMETHING_WENT_WRONG)