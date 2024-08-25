from django.db import models

# Create your models here.

class Item(models.Model):
    ItemId = models.IntegerField(default=-1)
    Name = models.CharField(max_length=50)
    BaseValue = models.IntegerField(default=-1)
    CanNotBeSoldToGameShop = models.BooleanField(default=False)
    CanNotBeTraded = models.BooleanField(default=False)