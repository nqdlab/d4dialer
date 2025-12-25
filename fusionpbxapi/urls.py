from django.urls import path
from .views import FusionpbxApiHandler

urlpatterns = [
    path('', FusionpbxApiHandler.as_view(), name='fusionpbxapi'),
]
