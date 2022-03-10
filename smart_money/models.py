from django.db import models

# Create your models here.
class Instrument(models.Model):
    ticker = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    market = models.CharField(max_length=20)
    
    def __str__(self):
        return f'{self.ticker}'