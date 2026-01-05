import requests 
import threading
from django.db import connections
from . import dbhandler

def start_campaign(campaign_uuid):
    campaign_ivr_menu_start = dbhandler.get_ivr_in_campaign(campaign_uuid)
    campaign_concurrent_calls = dbhandler.get_concurrent_calls_in_campaign(campaign_uuid)
    phone_numbers = dbhandler.get_phone_numbers_in_campaign(campaign_uuid)
    gateway_name = dbhandler.get_gateway_in_campaign(campaign_uuid)
    gateway_uuid = dbhandler.get_sip_gateway_uuid(gateway_name)
    counter = 0
    taskList = []

    if campaign_ivr_menu_start:       
        ivr_menu_extension = dbhandler.get_ivr_menu_extension(campaign_ivr_menu_start)
        domain_uuid = dbhandler.get_domain_uuid(campaign_ivr_menu_start)
        domain_name = dbhandler.get_domain_name(domain_uuid)
        api_keys = dbhandler.get_api_keys()

        dbhandler.update_campaign_status(campaign_uuid,'IN PROGRESS')

        for phone_number in phone_numbers:
            task = threading.Thread(target=originate_call, args=(campaign_uuid, phone_number, ivr_menu_extension, domain_name, gateway_uuid))
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
        dbhandler.update_campaign_status(campaign_uuid,'COMPLETED')

def originate_call(campaign_uuid, phone_number, ivr_menu_extension, domain_name, gateway_uuid):    
    api_keys = dbhandler.get_api_keys()

    url = "http://127.0.0.1:8000/api/fusionpbx/"
    payload = { 
        "token": api_keys[0], 
        "action": "originate", 
        "endpoint": f"{phone_number}", 
        "destination": f"{ivr_menu_extension}", 
        "domain": f"{domain_name}",
        "gateway_uuid": f"{gateway_uuid}"
        }
    response = requests.post(url, json=payload)
    reason = response.json().get("reason")
    dbhandler.update_campaign_lead_status(campaign_uuid, phone_number, reason)
    return reason