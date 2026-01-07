from django.db import connections
from .models import Campaign, CampaignLead, D4Settings
from django.db.utils import OperationalError, ConnectionDoesNotExist

#Django internal databases access functions
def get_d4settings():
    return D4Settings.objects.first()

def update_d4settings_voip_platform(platform):
    D4Settings.objects.all().update(voip_platform=platform)

def update_d4settings_voip_platform_db_engine(engine):
    D4Settings.objects.all().update(voip_platform_db_engine=engine)

def update_d4settings_voip_platform_db_name(name):
    D4Settings.objects.all().update(voip_platform_db_name=name)

def update_d4settings_voip_platform_db_user(user):
    D4Settings.objects.all().update(voip_platform_db_user=user)

def update_d4settings_voip_platform_db_password(password):
    D4Settings.objects.all().update(voip_platform_db_password=password)

def update_d4settings_voip_platform_db_host(host):
    D4Settings.objects.all().update(voip_platform_db_host=host)

def update_d4settings_voip_platform_db_port(port):
    D4Settings.objects.all().update(voip_platform_db_port=port)

def check_db_connection(custom_db):
    try:
        connections[custom_db].ensure_connection()
        return True
    except (OperationalError, ConnectionDoesNotExist):
        return False

def get_campaigns():
    return Campaign.objects.all()

def get_campaign(campaign_uuid):
    return Campaign.objects.get(campaign_uuid=campaign_uuid)

def get_campaign_status(campaign_uuid):
    campaign = Campaign.objects.get(campaign_uuid=campaign_uuid)
    return campaign.campaign_status

def get_ivr_in_campaign(campaign_uuid):
    return Campaign.objects.filter(campaign_uuid=campaign_uuid).values_list("campaign_ivr_menu", flat=True).first()

def get_concurrent_calls_in_campaign(campaign_uuid):
    return Campaign.objects.filter(campaign_uuid=campaign_uuid).values_list("campaign_concurrent_calls", flat=True).first()

def get_gateway_in_campaign(campaign_uuid):
    return Campaign.objects.filter(campaign_uuid=campaign_uuid).values_list("campaign_sip_gateway", flat=True).first()

def get_campaign_leads(campaign_uuid):
    return CampaignLead.objects.filter(campaign__campaign_uuid=campaign_uuid).values("phone_number", "status")   

def get_phone_numbers_in_campaign(campaign_uuid):
    return CampaignLead.objects.filter( campaign__campaign_uuid=campaign_uuid ).values_list("phone_number", flat=True)

def delete_campaigns(campaign_ids):
    Campaign.objects.filter(id__in=campaign_ids).delete()

def delete_campaign_lead(campaign_uuid, phone_number):
    CampaignLead.objects.filter(campaign__campaign_uuid=campaign_uuid, phone_number=phone_number).delete()

def create_campaign(campaign_uuid, campaign_name, campaign_ivr_menu, campaign_concurrent_calls, campaign_sip_gateway):
    return Campaign.objects.create(
                    campaign_uuid=campaign_uuid,                    
                    campaign_name=campaign_name,
                    campaign_ivr_menu=campaign_ivr_menu,
                    campaign_concurrent_calls=campaign_concurrent_calls,
                    campaign_sip_gateway=campaign_sip_gateway
                )

def is_number_in_campaign(campaign_uuid, phone_number):
    return CampaignLead.objects.filter(campaign__campaign_uuid=campaign_uuid, phone_number=phone_number).exists()

def create_campaign_lead(campaign, phone_number):
    return CampaignLead.objects.create(
        campaign=campaign,
        phone_number=phone_number
    )

def update_campaign_lead_status(campaign_uuid, phone_number, status):
    CampaignLead.objects.filter(campaign__campaign_uuid=campaign_uuid, phone_number=phone_number).update(status=status)
    
def update_campaign_status(campaign_uuid, status):
    Campaign.objects.filter(campaign_uuid=campaign_uuid).update(campaign_status=status)

#FusionPBX database access functions

def execute(cmd):
    cursor = connections['fusionpbx'].cursor()
    cursor.execute(cmd)
    rows = cursor.fetchall()
    return rows

def get_ivr_menu_names():
    rows =  execute("select ivr_menu_name from v_ivr_menus;")
    return [r[0] for r in rows]

def get_sip_gateway_names():
    rows =  execute("select gateway from v_gateways;")
    return [r[0] for r in rows]

def get_sip_gateway_uuid(gateway_name):
    rows =  execute(f"select gateway_uuid from v_gateways where gateway='{gateway_name}';")
    return rows[0][0] if rows else None

def get_ivr_menu_extension(ivr_menu_name):
    rows = execute(f"select ivr_menu_extension from v_ivr_menus where ivr_menu_name='{ivr_menu_name}';")
    if rows:
        return rows[0][0]
    return None

def get_domain_uuid(ivr_menu_name):
    rows = execute(f"select domain_uuid from v_ivr_menus where ivr_menu_name='{ivr_menu_name}';")
    if rows:
        return rows[0][0]
    return None

def get_domain_name(domain_uuid):
    rows = execute(f"select domain_name from v_domains where domain_uuid='{domain_uuid}';")
    if rows:
        return rows[0][0]
    return None

def get_api_keys():
    rows = execute("select api_key from v_users;")
    return [r[0] for r in rows]