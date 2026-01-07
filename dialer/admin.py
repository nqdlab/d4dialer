from django.contrib import admin
from .models import Campaign, CampaignLead, D4Settings

admin.site.register(CampaignLead) 
admin.site.register(Campaign)
admin.site.register(D4Settings)
