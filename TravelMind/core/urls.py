from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/destinations/', include('destinations.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/recommendations/', include('recommendations.urls')),
]