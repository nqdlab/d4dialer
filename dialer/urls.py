from django.urls import path
from .views import DialerHome

urlpatterns = [        
    path('', DialerHome.as_view(), name='dialer'),
]

