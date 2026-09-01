from django.contrib import admin
from .models import RecommendationHistory


@admin.register(RecommendationHistory)
class RecommendationHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'result_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    readonly_fields = ['user', 'preferences_snapshot', 'results_snapshot', 'result_count', 'created_at']

    def has_add_permission(self, request):
        return False
