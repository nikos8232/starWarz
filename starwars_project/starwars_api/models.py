from django.db import models

class Film(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    episode_id = models.IntegerField()
    film_id = models.IntegerField(default=None)
    release_date = models.DateField()

class Character(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    height = models.IntegerField()
    mass = models.IntegerField()
    films = models.ManyToManyField(Film, related_name='characters')

class Starship(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    length = models.FloatField()
    crew = models.IntegerField()
    passengers = models.CharField(max_length=10, blank=True, default='N/A')
    films = models.ManyToManyField(Film, related_name='starship')

class Vote(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, null=True, blank=True)
    film = models.ForeignKey(Film, on_delete=models.CASCADE, null=True, blank=True)
    starship = models.ForeignKey(Starship, on_delete=models.CASCADE, null=True, blank=True)
    voter_ip = models.GenericIPAddressField()  # Store IP to prevent multiple votes from the same user

    class Meta:
        unique_together = ('character', 'film', 'starship', 'voter_ip')
