from django.urls import path
from .views import get_image

urlpatterns = [
    path('api/get-image/', get_image, name='get_image'),
]
