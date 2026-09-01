from rest_framework import serializers
from .models import TravelCategory, Season


class TravelCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelCategory
        fields = ['id', 'slug', 'name', 'name_mk', 'icon', 'order']


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['id', 'slug', 'name', 'name_mk', 'order']
