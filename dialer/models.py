from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class D4Settings(models.Model):
    voip_platform = models.CharField(max_length=255, null=True, blank=True)
    voip_platform_db_engine = models.CharField(max_length=255, null=True, blank=True)
    voip_platform_db_name = models.CharField(max_length=255, null=True, blank=True)
    voip_platform_db_user = models.CharField(max_length=255, null=True, blank=True)
    voip_platform_db_password = models.CharField(max_length=255, null=True, blank=True)
    voip_platform_db_host = models.CharField(max_length=255, null=True, blank=True)
    voip_platform_db_port = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return self.voip_platform

class FreeswitchEsl(models.Model):
    event_socket_ip = models.GenericIPAddressField( 
        protocol='both', 
        unpack_ipv4=True, 
        null=True, 
        blank=True 
        )
    event_socket_port = models.PositiveIntegerField()
    event_socket_password = models.CharField(max_length=128)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.event_socket_ip

class Campaign(models.Model):
    campaign_uuid = models.CharField(max_length=255, unique=True)
    campaign_name = models.CharField(max_length=255)
    campaign_ivr_menu = models.CharField(max_length=255, null=True, blank=True)
    campaign_sip_gateway = models.CharField(max_length=255, null=True, blank=True)
    campaign_concurrent_calls = models.IntegerField(default=1)
    campaign_status = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.campaign_uuid

class CampaignLead(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='leads')
    phone_number = models.CharField(max_length=32)
    status = models.CharField(max_length=32, null=True, blank=True)

    class Meta: 
        constraints = [ 
            models.UniqueConstraint(fields=['campaign', 'phone_number'], name='unique_lead_per_campaign') 
            ]

    def __str__(self):
        return f"{self.campaign.campaign_uuid} - {self.phone_number}"