from decimal import Decimal

import requests
from starwars_api.models import Film, Character, Starship

SWAPI_URL = 'https://swapi.dev/api'

film_obj = Film.objects
character_obj = Character.objects
starship_obj = Starship.objects

def fetch_and_store_data():
    fetch_films()
    fetch_characters()
    fetch_starships()

def fetch_films():
    response = requests.get(f"{SWAPI_URL}/films/")
    films = response.json()['results']
    for film in films:
        film_obj.update_or_create(
            title=film['title'],
            episode_id=film['episode_id'],
            film_id=film['url'].split("/")[-2],
            release_date=film['release_date']
        )

def fetch_characters():
    response = requests.get(f"{SWAPI_URL}/people/")
    characters = response.json()['results']
    for character in characters:
        saved_character, created = character_obj.update_or_create(
            name=character['name'],
            height=character['height'],
            mass=character['mass']
        )
        for film_url in character['films']:
            film_id = film_url.split("/")[-2]
            film = Film.objects.get(film_id=film_id)
            saved_character.films.add(film)

        saved_character.save()

def fetch_starships():
    response = requests.get(f"{SWAPI_URL}/starships/")
    starships = response.json()['results']
    for starship in starships:

        starship_crew = starship["crew"]
        if "-" in starship_crew:
            starship_crew = starship_crew.split("-")[1]
        elif "," in starship_crew:
            starship_crew = starship_crew.split(",")[0]

        starship_length = starship['length']
        if "," in starship_length:
            starship_length = starship_length.replace(',', '')

        starship_crew = int(starship_crew)
        saved_starship, created = starship_obj.update_or_create(
            name=starship['name'],
            model=starship['model'],
            manufacturer=starship['manufacturer'],
            length=starship_length,
            crew=starship_crew,
            passengers=starship['passengers']
        )
        for film_url in starship['films']:
            film_id = film_url.split("/")[-2]
            film = Film.objects.get(film_id=film_id)
            saved_starship.films.add(film)
        saved_starship.save()