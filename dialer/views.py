from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connections
import json
import uuid
import requests
import threading
from django.http import JsonResponse
from .models import Campaign, CampaignLead
from .tasks import start_campaign
from . import dbhandler

class DialerHome(View):
    def get(self, request, *args, **kwargs): 
        campaigns = Campaign.objects.all()         
        ivr_menu_names = dbhandler.get_ivr_menu_names()
        sip_gateway_names = dbhandler.get_sip_gateway_names()
        return render(request, "dialer.html", {
            "campaigns": campaigns, 
            "ivr_menu_names": ivr_menu_names,
            "sip_gateway_names": sip_gateway_names
            })

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', '')
        campaign_uuid = request.POST.get('campaign_uuid', '')
        campaign_ivr_menu = request.POST.get('campaign_ivr_menu', '')        
        campaign_uuid_start = request.POST.get('campaign_uuid_start', '')                

        if action == 'numbers_query':
            campaign_uuid_query = request.POST.get('campaign_uuid_query', '')
            leads = CampaignLead.objects.filter(campaign__campaign_uuid=campaign_uuid_query).values("phone_number", "status")
            return JsonResponse(list(leads), safe=False)

        if action == 'save':            
            campaign_concurrent_calls = request.POST.get('campaign_concurrent_calls', 1)            
            campaign_sip_gateway = request.POST.get('campaign_sip_gateway', '')

            new_numbers_string = request.POST.get('new_numbers', '[]')
            if new_numbers_string == '':
                new_numbers_string = '[]'
            new_numbers = json.loads(new_numbers_string)

            deleted_numbers_string = request.POST.get('deleted_numbers', '[]')
            if deleted_numbers_string == '':
                deleted_numbers_string = '[]'
            deleted_numbers = json.loads(deleted_numbers_string)

            if not campaign_uuid:
                # Create a new campaign if no UUID provided
                campaign_uuid = str(uuid.uuid4())
                campaign_name = f"Campaign {campaign_uuid[:8]}"
                campaign = Campaign.objects.create(
                    campaign_uuid=campaign_uuid,                    
                    campaign_name=campaign_name,
                    campaign_ivr_menu=campaign_ivr_menu,
                    campaign_concurrent_calls=campaign_concurrent_calls,
                    campaign_sip_gateway=campaign_sip_gateway
                )
                for number in new_numbers:
                    CampaignLead.objects.create(
                        campaign=campaign,
                        phone_number=number
                    )

                for number in deleted_numbers:
                    CampaignLead.objects.filter(campaign__campaign_uuid=campaign_uuid, phone_number=number).delete()

            else:            
                campaign = Campaign.objects.get(campaign_uuid=campaign_uuid)
                campaign.campaign_ivr_menu = campaign_ivr_menu
                campaign.campaign_concurrent_calls = campaign_concurrent_calls
                campaign.campaign_sip_gateway = campaign_sip_gateway
                campaign.save()
                for number in new_numbers:
                    if CampaignLead.objects.filter(campaign__campaign_uuid=campaign_uuid, phone_number=number).exists():
                        continue
                    CampaignLead.objects.create(
                            campaign=campaign,
                            phone_number=number
                        )

                for number in deleted_numbers:
                    CampaignLead.objects.filter(campaign__campaign_uuid=campaign_uuid, phone_number=number).delete()

            campaigns = Campaign.objects.all()

        if action == 'delete':
            campaign_ids = request.POST.getlist('campaign_ids')
            Campaign.objects.filter(id__in=campaign_ids).delete()

        if action == 'start':            
            if campaign_uuid_start:                                    
                task = threading.Thread(target=start_campaign, args=(campaign_uuid_start,))
                task.start()                

        ivr_menu_names = dbhandler.get_ivr_menu_names()
        sip_gateway_names = dbhandler.get_sip_gateway_names()
        campaigns = Campaign.objects.all()
        return render(request, "dialer.html", {
            "campaigns": campaigns, 
            "ivr_menu_names": ivr_menu_names,
            "sip_gateway_names": sip_gateway_names
        })