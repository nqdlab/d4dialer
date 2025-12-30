import requests 
from .models import Campaign, CampaignLead

def originate_call(campaign_ivr_menu_start, phone_number, ivr_menu_extension, domain_name):
    url = "http://127.0.0.1:8000/api/fusionpbx/"
    payload = { 
        "token": "BqjUiAKGUP7kZTUYj13X9pvxMXULD0ev", 
        "action": "originate", 
        "endpoint": f"{phone_number}", 
        "destination": f"{ivr_menu_extension}", 
        "domain": f"{domain_name}" 
        }
    response = requests.post(url, json=payload)
    reason = response.json().get("reason")
    CampaignLead.objects.filter( campaign__campaign_uuid=campaign_ivr_menu_start, phone_number=phone_number ).update( status=reason )
    return reason