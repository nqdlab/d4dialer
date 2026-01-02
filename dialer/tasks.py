import requests 
import threading
from .models import Campaign, CampaignLead
from django.db import connections
from . import dbhandler

def start_campaign(campaign_uuid):
    campaign_ivr_menu_start = Campaign.objects.filter(campaign_uuid=campaign_uuid).values_list("campaign_ivr_menu", flat=True).first()
    campaign_concurrent_calls = Campaign.objects.filter(campaign_uuid=campaign_uuid).values_list("campaign_concurrent_calls", flat=True).first()
    phone_numbers = CampaignLead.objects.filter( campaign__campaign_uuid=campaign_uuid ).values_list("phone_number", flat=True)
    counter = 0
    taskList = []

    if campaign_ivr_menu_start:       
        ivr_menu_extension = dbhandler.get_ivr_menu_extension(campaign_ivr_menu_start)
        domain_uuid = dbhandler.get_domain_uuid(campaign_ivr_menu_start)
        domain_name = dbhandler.get_domain_name(domain_uuid)
        api_keys = dbhandler.get_api_keys()

        for phone_number in phone_numbers:
            task = threading.Thread(target=originate_call, args=(campaign_uuid, phone_number, ivr_menu_extension, domain_name))
            task.start()
            taskList.append(task)
            counter += 1
            if counter == int(campaign_concurrent_calls):
                tasks_in_progress = True
                while tasks_in_progress:
                    # Check for completed threads
                    for task in taskList:
                        if not task.is_alive():                                        
                            taskList.remove(task)
                            counter -= 1
                            tasks_in_progress = False
                            break  

def originate_call(campaign_uuid, phone_number, ivr_menu_extension, domain_name):    
    api_keys = dbhandler.get_api_keys()

    url = "http://127.0.0.1:8000/api/fusionpbx/"
    payload = { 
        "token": api_keys[0], 
        "action": "originate", 
        "endpoint": f"{phone_number}", 
        "destination": f"{ivr_menu_extension}", 
        "domain": f"{domain_name}" 
        }
    response = requests.post(url, json=payload)
    reason = response.json().get("reason")
    CampaignLead.objects.filter( campaign__campaign_uuid=campaign_uuid, phone_number=phone_number ).update( status=reason )    
    return reason