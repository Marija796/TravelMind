from django.conf import settings
from django.db import models


class RecommendationHistory(models.Model):
    """
    One row per authenticated recommendation search (RecommendationView.get()).
    Stores a preference snapshot and a ranked-results snapshot as JSON rather
    than FKs, so a later profile edit doesn't retroactively change what a
    past search "was", and a destination being edited/deleted later doesn't
    break history display.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendation_history',
    )
    preferences_snapshot = models.JSONField(default=dict)
    results_snapshot = models.JSONField(default=list)
    result_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Recommendation history'

    def __str__(self):
        return f"{self.user.username} - {self.created_at:%Y-%m-%d %H:%M}"
