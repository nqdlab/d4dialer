from django.db import models

class Campaign(models.Model):
    campaign_uuid = models.CharField(max_length=255, unique=True)
    campaign_name = models.CharField(max_length=255)
    campaign_ivr_menu = models.CharField(max_length=255, null=True, blank=True)
    campaign_sip_gateway = models.CharField(max_length=255, null=True, blank=True)
    campaign_concurrent_calls = models.IntegerField(default=1)

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