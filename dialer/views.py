from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connections
import json
import uuid
from .models import Campaign, CampaignLead

class DialerHome(View):
    def get(self, request, *args, **kwargs): 
        campaigns = Campaign.objects.prefetch_related('leads').all()
        cursor = connections['fusionpbx'].cursor()
        cursor.execute("select ivr_menu_name from v_ivr_menus;")
        rows = cursor.fetchall()
        ivr_menu_names = [r[0] for r in rows]
        return render(request, "dialer.html", {"campaigns": campaigns, "ivr_menu_names": ivr_menu_names})

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', '')
        numbers_json = request.POST.get('numbers', '[]')
        campaign_uuid = request.POST.get('campaign_uuid', '')
        campaign_ivr_menu = request.POST.get('campaign_ivr_menu', '')
        removed_numbers_json = request.POST.get('removed_numbers', '[]')

        try:
            numbers = json.loads(numbers_json)
        except json.JSONDecodeError:
            numbers = []

        cursor = connections['fusionpbx'].cursor()
        cursor.execute("select ivr_menu_name from v_ivr_menus;")
        rows = cursor.fetchall()
        ivr_menu_names = [r[0] for r in rows]

        if action == 'save':
            if not campaign_uuid:
                # Create a new campaign if no UUID provided
                campaign_uuid = str(uuid.uuid4())
                campaign_name = f"Campaign {campaign_uuid[:8]}"
                campaign = Campaign.objects.create(
                    campaign_uuid=campaign_uuid,                    
                    campaign_name=campaign_name,
                    campaign_ivr_menu=campaign_ivr_menu
                )
                for number in numbers:
                    CampaignLead.objects.create(
                        campaign=campaign,
                        phone_number=number
                    )
            else:            
                campaign = Campaign.objects.get(campaign_uuid=campaign_uuid)
                campaign.campaign_ivr_menu = campaign_ivr_menu
                campaign.save()
                CampaignLead.objects.filter(campaign=campaign).delete()
                for number in numbers:
                    if number not in json.loads(removed_numbers_json):
                        CampaignLead.objects.create(
                            campaign=campaign,
                            phone_number=number
                        )

            campaigns = Campaign.objects.prefetch_related('leads').all()

        if action == 'delete':
            campaign_ids = request.POST.getlist('campaign_ids')
            Campaign.objects.filter(id__in=campaign_ids).delete()

        campaigns = Campaign.objects.prefetch_related('leads').all()

        return render(request, "dialer.html", {"campaigns": campaigns, "ivr_menu_names": ivr_menu_names})