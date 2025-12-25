from django.views import View
from django.shortcuts import render

class DialerHome(View):
    def get(self, request, *args, **kwargs): 
        return render(request, "dialer.html")
