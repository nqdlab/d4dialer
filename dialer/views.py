from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connections
import json
import uuid
import requests
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
        campaign_uuid_start = request.POST.get('campaign_uuid_start', '')
        campaign_concurrent_calls = request.POST.get('campaign_concurrent_calls', 1)
        call_status = []

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
                    campaign_ivr_menu=campaign_ivr_menu,
                    campaign_concurrent_calls=campaign_concurrent_calls
                )
                for number in numbers:
                    CampaignLead.objects.create(
                        campaign=campaign,
                        phone_number=number
                    )
            else:            
                campaign = Campaign.objects.get(campaign_uuid=campaign_uuid)
                campaign.campaign_ivr_menu = campaign_ivr_menu
                campaign.campaign_concurrent_calls = campaign_concurrent_calls
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

        if action == 'start':
            if campaign_uuid_start:
                campaign_ivr_menu_start = Campaign.objects.filter(campaign_uuid=campaign_uuid_start).values_list("campaign_ivr_menu", flat=True).first()
                if campaign_ivr_menu_start:
                    cursor = connections['fusionpbx'].cursor()
                    cursor.execute(f"select ivr_menu_extension from v_ivr_menus where ivr_menu_name='{campaign_ivr_menu_start}';")
                    rows = cursor.fetchall()
                    ivr_menu_extension = rows[0][0]
                    cursor.execute(f"select domain_uuid from v_ivr_menus where ivr_menu_name='{campaign_ivr_menu_start}';")
                    rows = cursor.fetchall()
                    domain_uuid = rows[0][0]
                    cursor.execute(f"select domain_name from v_domains where domain_uuid='{domain_uuid}';")
                    rows = cursor.fetchall()
                    domain_name = rows[0][0]

                    phone_numbers = CampaignLead.objects.filter( campaign__campaign_uuid=campaign_uuid_start ).values_list("phone_number", flat=True)

                    for phone_number in phone_numbers:                    
                        url = "http://127.0.0.1:8000/api/fusionpbx/"
                        payload = { 
                            "token": "BqjUiAKGUP7kZTUYj13X9pvxMXULD0ev", 
                            "action": "originate", 
                            "endpoint": f"{phone_number}", 
                            "destination": f"{ivr_menu_extension}", 
                            "domain": f"{domain_name}" 
                            }
                        response_originate = requests.post(url, json=payload)
                        call_status = {
                            "reason": response_originate.json().get("reason"),
                            "campaign_uuid": campaign_uuid_start
                        }
                else:
                    call_status = {
                        "reason": "NO_IVR_MENU_SET",
                        "campaign_uuid": campaign_uuid_start
                    }

        campaigns = Campaign.objects.prefetch_related('leads').all()        
        return render(request, "dialer.html", {
            "campaigns": campaigns, 
            "ivr_menu_names": ivr_menu_names,
            "call_status": call_status
            })