from django.db import models
from django.conf import settings
from destinations.models import Destination

class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'destination')

    def __str__(self):
        return f"{self.user.username} - {self.destination.name} ({self.rating}★)"