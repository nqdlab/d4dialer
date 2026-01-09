from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connections
from django.conf import settings
import json
import uuid
import requests
import threading
import importlib 
import pathlib
import re
import time
from django.http import JsonResponse
from .tasks import start_campaign
from . import dbhandler, const
from fusionpbxapi.views import FusionpbxApiHandler

class DialerHome(View):
    def get(self, request, *args, **kwargs): 
        returnData = {}
        d4settings = dbhandler.get_d4settings()
        voip_platform = d4settings.voip_platform
        db_connection = dbhandler.check_db_connection(voip_platform)
        returnData["db_connection"] = db_connection
        
        if voip_platform == 'fusionpbx':
            api_connection = FusionpbxApiHandler.get_esl_connection(
                d4settings.voip_platform_api_host, 
                d4settings.voip_platform_api_port, 
                d4settings.voip_platform_api_password).connected()            
        else:
            api_connection = 0
        
        returnData["api_connection"] = api_connection
    
        if db_connection:
            if api_connection:
                campaigns = dbhandler.get_campaigns()
                ivr_menu_names = dbhandler.get_ivr_menu_names()
                sip_gateway_names = dbhandler.get_sip_gateway_names()
                                
                returnData["voip_platform"] = voip_platform
                returnData["campaigns"] = campaigns
                returnData["ivr_menu_names"] = ivr_menu_names
                returnData["sip_gateway_names"] = sip_gateway_names
                return render(request, "dialer.html", returnData)
        
        return render(request, "dialer.html", returnData)

    def post(self, request, *args, **kwargs):
        returnData = {}
        d4settings = dbhandler.get_d4settings()
        voip_platform = d4settings.voip_platform
        db_connection = dbhandler.check_db_connection(voip_platform)
        returnData["db_connection"] = db_connection
        action = request.POST.get('action', '')                     

        if voip_platform == 'fusionpbx':
            api_connection = FusionpbxApiHandler.get_esl_connection(
                d4settings.voip_platform_api_host, 
                d4settings.voip_platform_api_port, 
                d4settings.voip_platform_api_password).connected()
        else:
            api_connection = 0

        if action == 'd4dialer_settings_save':
            voip_platform = request.POST.get('voip_platform', '')
            voip_platform_db_user = request.POST.get('voip_platform_db_user', '')
            voip_platform_db_password = request.POST.get('voip_platform_db_password', '')
            voip_platform_db_host = request.POST.get('voip_platform_db_host', '')
            voip_platform_db_port = request.POST.get('voip_platform_db_port', '')
            voip_platform_db_engine = const.FUSIONPBX_DB["ENGINE"]
            voip_platform_db_name = const.FUSIONPBX_DB["NAME"]      

            dbhandler.update_d4settings_voip_platform(voip_platform)
            dbhandler.update_d4settings_voip_platform_db_engine(voip_platform_db_engine)
            dbhandler.update_d4settings_voip_platform_db_name(voip_platform_db_name)
            dbhandler.update_d4settings_voip_platform_db_user(voip_platform_db_user)
            dbhandler.update_d4settings_voip_platform_db_password(voip_platform_db_password)
            dbhandler.update_d4settings_voip_platform_db_host(voip_platform_db_host)
            dbhandler.update_d4settings_voip_platform_db_port(voip_platform_db_port)                

            voip_platform_api_host = request.POST.get('voip_platform_api_host', '')
            voip_platform_api_port = request.POST.get('voip_platform_api_port', '')
            voip_platform_api_password = request.POST.get('voip_platform_api_password', '')

            dbhandler.update_d4settings_voip_platform_api_host(voip_platform_api_host)
            dbhandler.update_d4settings_voip_platform_api_port(voip_platform_api_port)
            dbhandler.update_d4settings_voip_platform_api_password(voip_platform_api_password)                  
            
            db_connection = dbhandler.check_db_connection(voip_platform)   
            returnData["db_connection"] = db_connection 
            if voip_platform == 'fusionpbx':
                api_connection = FusionpbxApiHandler.get_esl_connection(
                    d4settings.voip_platform_api_host, 
                    d4settings.voip_platform_api_port, 
                    d4settings.voip_platform_api_password).connected()  
            else:
                 api_connection = 0
        
        elif action == 'd4dialer_settings_platform_config_default_query':
            voip_platform = request.POST.get('voip_platform', '')
            if voip_platform == 'fusionpbx':
                voip_platform_database = const.FUSIONPBX_DB
                voip_platform_api = const.FUSIONPBX_ESL
            else:
                voip_platform_database = {}
                voip_platform_api = {}
            return JsonResponse({ 
                "voip_platform_database": voip_platform_database,
                "voip_platform_api": voip_platform_api,
            })

        elif action == 'd4dialer_settings_platform_config_query':
            d4settings = dbhandler.get_d4settings()
            voip_platform_database = {}            
            voip_platform_database["voip_platform"] = d4settings.voip_platform
            voip_platform_database["voip_platform_db_engine"] = d4settings.voip_platform_db_engine
            voip_platform_database["voip_platform_db_name"] = d4settings.voip_platform_db_name
            voip_platform_database["voip_platform_db_user"] = d4settings.voip_platform_db_user
            voip_platform_database["voip_platform_db_password"] = d4settings.voip_platform_db_password
            voip_platform_database["voip_platform_db_host"] = d4settings.voip_platform_db_host
            voip_platform_database["voip_platform_db_port"] = d4settings.voip_platform_db_port

            voip_platform_api = {}
            voip_platform_api["voip_platform_api_user"] = d4settings.voip_platform_api_user
            voip_platform_api["voip_platform_api_password"] = d4settings.voip_platform_api_password
            voip_platform_api["voip_platform_api_host"] = d4settings.voip_platform_api_host
            voip_platform_api["voip_platform_api_port"] = d4settings.voip_platform_api_port

            return JsonResponse({ 
                "voip_platform_database": voip_platform_database,
                "voip_platform_api": voip_platform_api,
            })

        elif action == 'campaign_query':
            campaign_uuid_query = request.POST.get('campaign_uuid_query', '')
            leads = dbhandler.get_campaign_leads(campaign_uuid_query)
            campaign_status = dbhandler.get_campaign_status(campaign_uuid_query)
            return JsonResponse({ "leads": list(leads), "campaign_status": campaign_status })

        elif action == 'save':      
            campaign_uuid = request.POST.get('campaign_uuid', '')   
            campaign_ivr_menu = request.POST.get('campaign_ivr_menu', '')                      
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
                campaign = dbhandler.create_campaign(campaign_uuid, campaign_name, campaign_ivr_menu, 
                    campaign_concurrent_calls, campaign_sip_gateway)

                for number in new_numbers:
                    dbhandler.create_campaign_lead(campaign, number)

                for number in deleted_numbers:
                    dbhandler.delete_campaign_lead(campaign_uuid, number)

            else:            
                campaign = dbhandler.get_campaign(campaign_uuid)
                campaign.campaign_ivr_menu = campaign_ivr_menu
                campaign.campaign_concurrent_calls = campaign_concurrent_calls
                campaign.campaign_sip_gateway = campaign_sip_gateway
                campaign.save()
                for number in new_numbers:
                    if dbhandler.is_number_in_campaign(campaign_uuid, number):
                        continue        
                    dbhandler.create_campaign_lead(campaign, number)

                for number in deleted_numbers:
                    dbhandler.delete_campaign_lead(campaign_uuid, number)

            campaigns = dbhandler.get_campaigns()

        elif action == 'delete':
            campaign_ids = request.POST.getlist('campaign_ids')
            dbhandler.delete_campaigns(campaign_ids)

        elif action == 'start':    
            campaign_uuid_start = request.POST.get('campaign_uuid_start', '')          
            if campaign_uuid_start:     
                campaign_status = dbhandler.get_campaign_status(campaign_uuid_start)
                if not campaign_status == 'IN PROGRESS':
                    if not campaign_status == 'COMPLETED':
                        task = threading.Thread(target=start_campaign, args=(campaign_uuid_start,))
                        task.start()                

        if db_connection:            
            ivr_menu_names = dbhandler.get_ivr_menu_names()
            sip_gateway_names = dbhandler.get_sip_gateway_names()
            campaigns = dbhandler.get_campaigns()                
            returnData["api_connection"] = api_connection
            returnData["voip_platform"] = voip_platform
            returnData["campaigns"] = campaigns
            returnData["ivr_menu_names"] = ivr_menu_names
            returnData["sip_gateway_names"] = sip_gateway_names
        return render(request, "dialer.html", returnData)