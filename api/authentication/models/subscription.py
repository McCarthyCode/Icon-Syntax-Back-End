from django.db import models
from api.models import TimestampedModel


class Subscription(TimestampedModel):
    email = models.EmailField()
