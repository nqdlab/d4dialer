from django.contrib import admin
from .models import Campaign, CampaignLead

admin.site.register(CampaignLead) 
admin.site.register(Campaign)
